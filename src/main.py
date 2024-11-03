from gmail_service import GmailService
from openai_service import OpenAIClient

import base64
from email.mime.text import MIMEText
import conversation_handler

SENDER_EMAIL = "james.r.dawson70@gmail.com"

def main():

    gmail = GmailService()

    # Replace with your email and recipient's email

    # # Email details
    # subject = 'Test Email from Python Module using OpenAI'

    # # Optional: Path to the attachment file
    # attachment_path = None  # Set to 'path/to/your/file.ext' if needed

    # # Send the email

    # client = OpenAIClient('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')

    # # Define your prompt
    # prompt = "Write an email introducing yourself"

    # # Send the prompt and get the response
    # response = client.send_prompt(prompt)

    # Print the response
    # if response:
    #     print("Response from OpenAI:")
    #     gmail.send_email(
    #         sender=SENDER_EMAIL,
    #         to="john.r.doe90@gmail.com",
    #         subject=subject,
    #         message_text=response,
    #         attachment_file=attachment_path
    #     )
    # else:
    #     print("Failed to get a response.")
    conversation_handler.send_first_message("john.r.doe90@gmail.com", "Hello")

if __name__ == '__main__':
    main()