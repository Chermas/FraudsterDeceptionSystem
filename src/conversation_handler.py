from gmail_service import GmailService
from openai_service import OpenAIClient
import logging_service as logs
from datetime import datetime, timezone, timedelta
import os
from bisect import insort
from email.utils import parseaddr
import nlp
import honeytoken_service as honeytoken
import threading
import random


gmail = GmailService()
client = OpenAIClient()
NLP = nlp.PDFTriggerDetector()

queue = logs.load_queue_from_file()

queue_lock = threading.Lock()

def send_first_reply(sender, subject):
    """
    Send the first message to the recipient.
    :param sender: The sender's email address.
    :param subject: The subject of the email.
    """
    email_id = gmail.find_message_by_sender_and_subject(sender,subject)

    if email_id is None:
        print("Email not found.")
        return

    email = gmail.get_email_from_id(email_id)
    body = email.get('full_body')

    converted_date = datetime.fromtimestamp(int(email.get('internalDate')) / 1000, tz=timezone.utc)
    date = converted_date.strftime('%Y-%m-%d %H:%M:%S %Z')

    # date = converted_date.isoformat()

    conv_id = logs.create_new_conversation_log(sender)

    logs.add_to_log(conv_id, sender, body, date)

    response = generate_reply(body)
    if response is None:
        print("Failed to get a response.")
        return
    
    res = gmail.reply_to_email(email, response)
    if res is not None and res['id'] and res['labelIds']:
        logs.add_to_log(conv_id, "me", response, datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'))
    else:
        print("Failed to send the reply.")

def start_conversation(sender, subject, body):
    """
    Start a new conversation with the sender.
    :param sender: The sender's email address.
    :param subject: The subject of the email.
    :param body: The body of the email.
    """
    conv_id = logs.create_new_conversation_log(sender)

    converted_date = datetime.now()
    date = converted_date.strftime('%Y-%m-%d %H:%M:%S %Z')

    logs.add_to_log(conv_id, sender, body, date)

    response = generate_reply(body)
    if response is None:
        print("Failed to get a response.")
        return
    
    res = gmail.send_email(sender, subject, response)
    if res is not None and res['id'] and res['labelIds']:
        logs.add_to_log(conv_id, "me", response, datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'))
    else:
        print("Failed to send the reply.")


def get_new_emails():
    """
    Get new emails from the inbox.
    :return: The new emails.
    """
    return gmail.check_for_new_emails(include_spam=True)

def has_new_emails():
    """
    Check for new emails in the inbox.
    :return: True if new emails are present, False otherwise.
    """
    new_emails = get_new_emails()
    return len(new_emails) > 0

def get_queue():
    """
    Get the current response queue.
    :return: The response queue.
    """
    return queue

def generate_reply(body):
    """
    Generate a reply to the sender.
    :param email: The email to reply to.
    :return: The reply message.
    """
    response = client.answer_email(body)
    return response

def generate_reply_with_pdf(body):
    """
    Generate a reply to the sender with a PDF attachment.
    :param email: The email to reply to.
    :return: The reply message.
    """
    response = client.answer_email_with_pdf(body)
    return response

def handle_incoming_message(email):
    """
    Handle an incoming message from the sender.
    """
    conv_id = logs.get_conversation_id(email['sender'])

    converted_date = datetime.fromtimestamp(int(email['timestamp']) / 1000, tz=timezone.utc)
    date = converted_date.strftime('%Y-%m-%d %H:%M:%S %Z')

    res = gmail.mark_as_read('me', email['id'])
    if res == -1:
        print("Failed to mark the email as read.")
        return

    logs.add_to_log(conv_id, email['sender'], email['body'], date)

    add_email_to_queue(email['id'])


def send_response(email_id):
    """
    Handle an incoming message from the sender.
    """
    email = gmail.get_message_details('me',email_id)
    raw_sender = next((header['value'] for header in email['payload']['headers'] if header['name'] == 'From'), None)
    sender_email = parseaddr(raw_sender)[1]  # Extract only the email address    
    conv_id = logs.get_conversation_id(sender_email)

    body = gmail.get_latest_message_content(email)

    conv_length = logs.get_conversation_length(conv_id)

    if conv_length < 4:
        include_pdf = False
    else:
        include_pdf = NLP.analyze_email(body)

    if not include_pdf:
        response = generate_reply(body)

        if response is None:
            print("Failed to get a response.")
            return
    
        res = gmail.reply_to_email(email, response)
    else:
        response = generate_reply_with_pdf(body)

        if response is None:
            print("Failed to get a response.")
            return
    
        token, path = honeytoken.generate_pdf(body)

        logs.add_honeytoken_id(token, conv_id)

        res = gmail.reply_to_email_with_attachment(email, response, path, token)

    if res is not None and res['id'] and res['labelIds']:
        logs.add_to_log(conv_id, "me", response, datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z'))
        dequeue_email()
    else:
        print("Failed to send the reply.")

def has_conversation(sender):
    """
    Check if a conversation is in progress.
    :return: True if a conversation is in progress, False otherwise.
    """
    conv_id = logs.get_conversation_id(sender)
    return os.path.exists(f"../logs/{conv_id}.json")

def generate_response_time():
    """
    Generate a tentative response time based on the current time.
    :return: The tentative response time.
    """
    # Define the working hours
    start_hour = 9  # 9 AM
    end_hour = 20   # 8 PM

    # Get the current time and date
    now = datetime.now()
    current_hour = now.hour

    # Generate a random interval in minutes between 2 hours and 5 hours
    random_minutes = random.randint(180, 300)
    tentative_response_time = now + timedelta(minutes=random_minutes)

    # Adjust if the tentative response time falls outside the 9 AM - 8 PM window
    # Wrap to the next day's valid working hours if needed
    if tentative_response_time.hour < start_hour:
        # Set to 9 AM on the same day
        response_time = tentative_response_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    elif tentative_response_time.hour >= end_hour:
        # Set to 9 AM on the next day
        response_time = (tentative_response_time + timedelta(days=1)).replace(hour=start_hour, minute=0, second=0, microsecond=0)
    else:
        # Valid time within the window, keep it as is
        response_time = tentative_response_time

    return response_time

def add_email_to_queue(email_id):
    global queue
    with queue_lock:  # Ensure exclusive access
        queue = logs.load_queue_from_file()  # Reload the queue from the file

        # Generate a response time for this email
        response_time = generate_response_time()
        
        # Create a dictionary with email details
        email_entry = {"email_id": email_id, "response_time": response_time}
        
        # Insert email into the queue in a sorted position based on response time
        insort(queue, email_entry, key=lambda x: x["response_time"])

        print("Queue:" + str(queue))
        logs.save_queue_to_file(queue)  # Save the updated queue to the file

        print(f"Email {email_id} added to the queue for {response_time}")

def dequeue_email():
    global queue
    with queue_lock:  # Ensure exclusive access
        queue = logs.load_queue_from_file()  # Reload the queue from the file

        print("Dequeueing email " + str(queue))
        if len(queue) > 0:
            ret = queue.pop(0)
            print("Queue:" + str(queue))
            logs.save_queue_to_file(queue)  # Save the updated queue to the file
            print(f"Email {ret['email_id']} dequeued.")
            return ret
        return None
    