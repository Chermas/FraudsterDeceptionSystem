from gmail_service import GmailService
from openai_service import OpenAIClient
import logging_service as logs

gmail = GmailService()
client = OpenAIClient('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')

def send_first_message(sender, subject):
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

    response = generate_reply(body)
    if response is None:
        print("Failed to get a response.")
        return
    
    res = gmail.reply_to_email(email, response)
    if res is not None and res['id'] and res['labelIds']:
        logs.create_new_conversation_log(sender)
        logs.add_to_log(sender, response, )
    else:
        print("Failed to send the reply.")


def get_new_emails():
    """
    Get new emails from the inbox.
    :return: The new emails.
    """
    return gmail.check_for_new_emails(include_spam=True)

def check_for_new_emails():
    """
    Check for new emails in the inbox.
    :return: True if new emails are present, False otherwise.
    """
    new_emails = get_new_emails()
    return len(new_emails) > 0

def generate_reply(body):
    """
    Generate a reply to the sender.
    :param email: The email to reply to.
    :return: The reply message.
    """
    response = client.send_prompt(body)
    return response

def send_reply():
    """
    Send a reply to the sender.
    """
    pass

def has_conversation():
    """
    Check if a conversation is in progress.
    :return: True if a conversation is in progress, False otherwise.
    """
    pass

def generate_response_timestamp():
    """
    Generate a timestamp for the response.
    :return: The timestamp.
    """
    pass

def add_email_to_queue(email):
    """
    Add an email to the conversation queue.
    :param email: The email to add.
    """
    pass