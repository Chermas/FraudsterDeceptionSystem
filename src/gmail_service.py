from __future__ import print_function
import os
import base64
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import re
from email.utils import parseaddr

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailService:
    """A class to interact with the Gmail API."""

    def __init__(self):
        """
        Initialize the GmailService instance by authenticating and creating a service object.
        """
        # Use environment variables to determine paths for credentials and token files
        self.credentials_file = os.getenv('CREDENTIALS_FILE_PATH', 'credentials.json')
        self.token_file = os.getenv('TOKEN_FILE_PATH', 'token.json')

        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_file}")
        if not os.path.exists(self.token_file):
            raise FileNotFoundError(f"Token file not found at {self.token_file}")

        # Define the OAuth 2.0 scopes
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate using stored credentials and return a Gmail API service instance."""
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("Invalid credentials or token. Please generate a new token.")
        
            # Save updated credentials
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    def append_signature(self, body, token):
        """
        Appends the signature to the email body while preserving its formatting.
        
        Args:
            body (str): The email body.
            token (str): The token to include in the signature URL.
        
        Returns:
            str: The email body with the signature appended, preserving formatting.
        """
        # Convert body text to HTML, preserving line breaks
        formatted_body = body.replace("\n", "<br>")
        
        # Signature HTML
        signature = f"""
        <br><br>
        --<br>
        James R Dawson<br>
        Colorado<br>
        <a href="http://server.jdawsontech.com/{token}" target="_blank">jdawsontech.com</a>
        """
        
        return f"{formatted_body}{signature}"

    def create_message(self, to, subject, message_text, token):
        """
        Create an email message without attachments and include a clickable signature.
        
        Args:
            to (str): Recipient email address.
            subject (str): Email subject.
            message_text (str): The email body text.
            token (str): The token to include in the signature URL.
        
        Returns:
            dict: A dictionary containing the base64-encoded email message.
        """
        # Append the signature with the clickable token
        full_message = self.append_signature(message_text, token)

        # Create the email as HTML to support clickable links
        message = MIMEText(full_message, 'html')  # 'html' ensures the link is clickable
        message['to'] = to
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

    def send_email(self, to, subject, message_text, token, attachment_file=None):
        """Send an email with or without an attachment."""
        if attachment_file:
            message = self.create_message_with_attachment(to, subject, message_text, attachment_file)
        else:
            message = self.create_message(to, subject, message_text, token)
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

    def get_latest_message_content(self, message):
        """
        Extract the latest email content from the full message body and format newlines for JSON.
        
        Args:
            message: The full message content retrieved from Gmail.
            
        Returns:
            A string containing only the new message content, with properly formatted newlines.
        """
        # Extract the full body from the message
        full_body = message.get("full_body", "")

        # Regex to match the start of quoted replies (common patterns like "On [date], [name] wrote:")
        pattern = r"(On\s.*?wrote:)"
        split_body = re.split(pattern, full_body, maxsplit=1, flags=re.IGNORECASE)

        # Take only the latest content before the reply section
        latest_content = split_body[0].strip() if split_body else full_body

        # Replace `\r\n` with actual newlines for readability
        formatted_content = latest_content.replace("\r\n", "\n")

        return formatted_content

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

                # Extract the sender and format it as only the email address
                raw_sender = next((header['value'] for header in msg_details['payload']['headers'] if header['name'] == 'From'), None)
                sender_email = parseaddr(raw_sender)[1]  # Extract only the email address

                body = self.get_latest_message_content(msg_details)
                
                # Append the email with the full message body
                new_emails.append({
                    "id": msg_id,
                    "threadId": msg_details.get('threadId'),
                    "sender": sender_email,
                    "subject": next((header['value'] for header in msg_details['payload']['headers'] if header['name'] == 'Subject'), None),
                    "body": body,
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
    def reply_to_email(self, email, response_text, token=None):
        """
        Reply to an existing email message in the same thread and mark it as read if successful.
        
        Args:
            email: Dictionary containing the email details, including "id".
            response_text: The text content for the reply.
            token: Optional token to include in the signature as a clickable link.
            
        Returns:
            The response from the Gmail API if successful, otherwise None.
        """
        message = self.get_email_from_id(email["id"])

        try:
            thread_id = message['threadId']
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            message_id_header = headers.get('Message-ID')
            from_email = headers.get('From')
            
            if not from_email:
                print("Error: 'From' email address not found in the original message.")
                return None
            
            # Mark email as read
            res = self.mark_as_read('me', email['id'])
            if res == -1:
                print("Failed to mark the email as read.")
                return None
            
            # Add the signature with a clickable link if the token is provided
            if token:
                response_text = self.append_signature(response_text, token)

            subject = "Re: " + headers.get('Subject', '')

            # Create the reply message in HTML format
            reply_message = MIMEText(response_text, 'html')  # 'html' ensures the signature link works as intended
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

            print(f"Reply sent successfully! Message Id: {send_response}")

            return send_response
        except Exception as error:
            print(f"An error occurred: {error}")
            return None
        
    def reply_to_email_with_attachment(self, email, response_text, attachment_path, token=None):
        """
        Reply to an existing email message in the same thread with an attachment and a clickable signature.

        Args:
            email: Dictionary containing the email details, including "id".
            response_text: The text content for the reply.
            attachment_path: The file path of the attachment to include.
            token: Optional token to include in the signature as a clickable link.

        Returns:
            The response from the Gmail API if successful, otherwise None.
        """
        message = self.get_email_from_id(email["id"])

        try:
            thread_id = message['threadId']
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            message_id_header = headers.get('Message-ID')
            from_email = headers.get('From')
            
            if not from_email:
                print("Error: 'From' email address not found in the original message.")
                return None
            
            # Mark email as read
            res = self.mark_as_read('me', email['id'])
            if res == -1:
                print("Failed to mark the email as read.")
                return None

            # Add the signature with a clickable link if the token is provided
            if token:
                response_text = self.append_signature(response_text, token)

            subject = "Re: " + headers.get('Subject', '')

            # Create a multipart email message to include both HTML body and attachment
            reply_message = MIMEMultipart()
            reply_message['to'] = from_email
            reply_message['subject'] = subject
            reply_message['In-Reply-To'] = message_id_header
            reply_message['References'] = message_id_header

            # Attach the email body (HTML format with signature)
            body_part = MIMEText(response_text, 'html')
            reply_message.attach(body_part)

            # Attach the file
            content_type, encoding = mimetypes.guess_type(attachment_path)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)

            with open(attachment_path, 'rb') as f:
                file_data = f.read()
            attachment = MIMEBase(main_type, sub_type)
            attachment.set_payload(file_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
            reply_message.attach(attachment)

            # Encode the message
            raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode()

            # Send the reply within the original thread
            send_response = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message, 'threadId': thread_id}
            ).execute()

            print(f"Reply with attachment and signature sent successfully! Message Id: {send_response['id']}")
            return send_response
        except Exception as error:
            print(f"An error occurred while sending the reply with attachment and signature: {error}")
            return None



    def mark_as_read(self, user_id, msg_id):
        """Mark a message as read."""
        try:
            self.service.users().messages().modify(
                userId=user_id,
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return 0
        except Exception as error:
            return -1
