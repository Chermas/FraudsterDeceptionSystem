import time
import threading
from flask import Flask, request, jsonify
import conversation_handler
from gmail_service import GmailService
from openai_service import OpenAIClient
import logging_service as logs
from datetime import datetime

# Initialize services
gmail_service = GmailService()

# Shared variable to store the latest command to start a conversation
command_data = {"start_conversation": None}

# Set up Flask API for receiving commands
app = Flask(__name__)

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    """API endpoint to start a conversation with specified email and subject."""
    data = request.json
    email = data.get("email")
    subject = data.get("subject")
    if email and subject:
        conversation_handler.send_first_reply(email, subject)
        return jsonify({"status": "Conversation command received"}), 200
    else:
        return jsonify({"error": "Missing email or subject"}), 400

@app.route('/status', methods=['GET'])
def status():
    """API endpoint to check the system status."""
    status_info = conversation_handler.get_status()
    return jsonify(status_info), 200

@app.route('/send_first_email', methods=['POST'])
def send_first_email():
    """API endpoint to send the first email in a conversation."""
    data = request.json
    sender = data.get("sender")
    subject = data.get("subject")
    body = data.get("body")
    if sender and subject and body:
        conversation_handler.start_conversation(sender, subject, body)
        return jsonify({"status": "First email sent"}), 200
    else:
        return jsonify({"error": "Missing sender, subject, or body"}), 400

# Continuous monitoring loop
def monitor_emails():
    """Loop to continuously monitor emails and process commands."""
    while True:
        print("Checking for new emails...")
        # Perform email monitoring tasks if needed
        new_emails = gmail_service.check_for_new_emails()
        print(f"New emails: {len(new_emails)}")
        for email in new_emails:
            print(email['sender'])
            if conversation_handler.has_conversation(email['sender']):
                print(f"Conversation with {email['sender']} already exists.")
                # Process each new email if needed
                conversation_handler.handle_incoming_message(email)

        time.sleep(60)  # Adjust the frequency of the loop as needed

def send_emails():
    while True:
        queue = conversation_handler.get_queue()
        if len(queue) > 0 and datetime.now() >= queue[0]['response_time']:
            email = queue.pop(0)
            conversation_handler.send_response(email['email_id'])
    
        time.sleep(60)  # Adjust the frequency of the loop as needed

# Start the monitoring loop in a separate thread
monitor_thread = threading.Thread(target=monitor_emails)
monitor_thread.start()

# Start the email sending loop in a separate thread
send_thread = threading.Thread(target=send_emails)
send_thread.start()

# Run the Flask app in the main thread
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8005)
