from __future__ import print_function
import os
import base64
import mimetypes
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailService:
    """A class to interact with the Gmail API."""

    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        """
        Initialize the GmailService instance by authenticating and creating a service object.
        :param credentials_file: Path to the client secret file.
        :param token_file: Path to the token file.
        """
        # Define the OAuth 2.0 scopes
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate using stored credentials and return a Gmail API service instance."""
        if not os.path.exists(self.token_file):
            raise Exception("Token file not found. Run the manual authorization flow first.")
        
        creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        service = build('gmail', 'v1', credentials=creds)
        return service

    def create_message(self, sender, to, subject, message_text):
        """Create an email message without attachments."""
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        # Encode the message in base64 format
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def create_message_with_attachment(self, sender, to, subject, message_text, file_path):
        """Create an email message with an attachment."""
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        # Attach the email body
        msg = MIMEText(message_text)
        message.attach(msg)

        # Guess the MIME type of the file
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)

        # Attach the file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        attachment = MIMEBase(main_type, sub_type)
        attachment.set_payload(file_data)
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
        message.attach(attachment)

        # Encode the message in base64 format
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def send_message(self, user_id, message):
        """Send an email message via the Gmail API."""
        try:
            sent_message = self.service.users().messages().send(userId=user_id, body=message).execute()
            print(f'Email sent successfully! Message Id: {sent_message["id"]}')
            return sent_message
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def send_email(self, sender, to, subject, message_text, attachment_file=None):
        """Send an email with or without an attachment."""
        if attachment_file:
            message = self.create_message_with_attachment(sender, to, subject, message_text, attachment_file)
        else:
            message = self.create_message(sender, to, subject, message_text)
        return self.send_message('me', message)

    def list_messages(self, user_id='me', query=''):
        """List all messages of the user's mailbox matching the query."""
        try:
            response = self.service.users().messages().list(userId=user_id, q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])
            return messages
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def get_message_details(self, user_id, msg_id):
        """Get detailed information of a specific message, including the entire body content."""
        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
            
            # Extract message body
            body = ""
            if 'parts' in message['payload']:  # Handle multipart messages
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            else:  # Handle single-part messages
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
            
            # Add the full body content to the message details
            message['full_body'] = body
            return message
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def check_for_new_emails(self, user_id='me', query='is:unread', include_spam=False):
        """
        Check for new unread emails, optionally including spam, and return a list of email details.
        
        Args:
            user_id: The Gmail user ID (usually 'me').
            query: Search query to filter messages (default is 'is:unread' for unread messages).
            include_spam: Boolean indicating if spam emails should be included.
            
        Returns:
            A list of dictionaries, each containing details about a new email.
            If no new emails are found, returns an empty list.
        """
        if include_spam:
            query += ' in:spam'
        
        new_emails = []
        messages = self.list_messages(user_id=user_id, query=query)
        
        if messages:
            for message in messages:
                msg_id = message['id']
                msg_details = self.get_message_details(user_id, msg_id)
                
                # Append the email with the full message body
                new_emails.append({
                    "id": msg_id,
                    "threadId": msg_details.get('threadId'),
                    "sender": next((header['value'] for header in msg_details['payload']['headers'] if header['name'] == 'From'), None),
                    "subject": next((header['value'] for header in msg_details['payload']['headers'] if header['name'] == 'Subject'), None),
                    "body": msg_details.get('full_body'),  # Include the entire message body
                    "timestamp": msg_details.get('internalDate')
                })
        
        return new_emails

    def find_message_by_sender_and_subject(self, sender, subject):
        """
        Search for a message by sender and subject.
        
        Args:
            sender: The email address of the sender.
            subject: The subject of the email.
            
        Returns:
            The message ID of the first matching email, or None if no match is found.
        """
        query = f'from:{sender} subject:"{subject}"'
        messages = self.list_messages(query=query)
        if messages:
            return messages[0]['id']  # Return the ID of the first matched message
        else:
            print("No matching messages found.")
            return None
        
    def get_email_from_id(self, message_id):
        """
        Retrieve the email details based on the message ID.
        
        Args:
            message_id: The ID of the email message.
            
        Returns:
            A dictionary containing the email details, or None if the message is not found.
        """

        message = self.get_message_details('me', message_id)
        if message:
            return message
        else:
            print(f"Message with ID {message_id} not found.")
            return None

    # Include the reply_to_message function as defined previously
    def reply_to_email(self, message, response_text):
        """
        Reply to an existing email message in the same thread.
        
        Args:
            message_id: The ID of the message to reply to.
            response_text: The text content for the reply.
            
        Returns:
            The response from the Gmail API if successful, otherwise None.
        """
        try:           
            thread_id = message['threadId']
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            message_id_header = headers.get('Message-ID')
            from_email = headers.get('From')
            
            if not from_email:
                print("Error: 'From' email address not found in the original message.")
                return None
            
            subject = "Re: " + headers.get('Subject', '')

            # Create the reply message
            reply_message = MIMEText(response_text)
            reply_message['to'] = from_email
            reply_message['subject'] = subject
            reply_message['In-Reply-To'] = message_id_header
            reply_message['References'] = message_id_header

            # Encode the reply message
            raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode()

            # Send the reply within the original thread
            send_response = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message, 'threadId': thread_id}
            ).execute()

            print(f'Reply sent successfully! Message Id: {send_response}')
            return send_response
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
