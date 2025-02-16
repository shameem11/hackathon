import os
import base64
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define OAuth 2.0 Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    
    # Load saved credentials if they exist
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Refresh or request new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Access token refreshed.")
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
        else:
            logger.info("Requesting new OAuth token...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            
            # Automatically runs a local web server for authentication
            creds = flow.run_local_server(port=0)

        # Save the new credentials
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def get_emails(service):
    """Fetch unread emails from Gmail."""
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        
        if not messages:
            logger.info("No unread emails found.")
            return []

        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            email_from = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown')

            email_body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'body' in part and 'data' in part['body']:
                        email_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                email_body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

            emails.append({'from': email_from, 'body': email_body})

        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {e}")
        return []

if __name__ == "__main__":
    gmail_service = authenticate_gmail()
    unread_emails = get_emails(gmail_service)
    
    if unread_emails:
        logger.info(f"Unread Emails Found: {len(unread_emails)}")
        for email in unread_emails:
            print(f"From: {email['from']}\nBody: {email['body']}\n{'-'*50}")
    else:
        logger.info("No new unread emails.")
