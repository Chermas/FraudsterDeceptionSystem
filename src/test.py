from google_auth_oauthlib.flow import InstalledAppFlow
import json
import generatePDF as pdf

def generate_refresh_token(credentials_file='credentials.json', token_file='token.json'):
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

    pdf.generate_pdf(context, title, subtitle, section)

# Run this script once to create token.json
# generate_refresh_token()

# Generate a sample PDF
generate_pdf()
