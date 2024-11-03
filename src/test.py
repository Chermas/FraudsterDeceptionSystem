from google_auth_oauthlib.flow import InstalledAppFlow
import json

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

# Run this script once to create token.json
generate_refresh_token()