from google_auth_oauthlib.flow import InstalledAppFlow
import generatePDF as pdf
import os
import conversation_handler as ch

def generate_refresh_token():
    """
    Generate a new refresh token and save it to the token file.
    """
    # Use environment variables to determine paths
    credentials_file = os.getenv('CREDENTIALS_FILE_PATH', 'credentials.json')
    token_file = os.getenv('TOKEN_FILE_PATH', 'token.json')

    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found at {credentials_file}")

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save refresh token and credentials to file
    with open(token_file, 'w') as token:
        token.write(creds.to_json())
    print("Refresh token saved.")


def generate_pdf():
    context = "Hello James, some important information has come up on the investment opportunity we discussed. I will need some information from you"
    title = "Test Title"
    subtitle = "Test Subtitle"
    section = "Test Section"
    token = 'test_token'

    pdf.generate_pdf(token, context, title, subtitle, section)

def test_queue():
    ch.add_email_to_queue('test_id')
    ch.dequeue_email()

# Run this script once to create token.json
# generate_refresh_token()

# Generate a sample PDF
# generate_pdf()

# Test the email queue  
test_queue()

