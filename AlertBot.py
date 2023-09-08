import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from apiclient import errors
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# Replace with your own service account credentials JSON file
SERVICE_ACCOUNT_FILE = 'C:/Users/Felix Tong/OneDrive/Documents/AlertBot/docsalertbot-e063ebab1964.json'

# Replace with your own email address for alerting
authorized_emails = ['EagleEyeJZ1234@gmail.com', 'tongfelix000@gmail.com']
recipients = ['Jason', 'Felix']

# Define the scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

# Function to list recent changes to a document
def list_recent_changes(service, file_id, start_page_token):
    results = []
    while True:
        try:
            changes = service.changes().list(
                pageToken=start_page_token,  # Provide the page token here
                spaces='drive',
                fields='nextPageToken, changes',
                pageSize=1000  # Adjust the page size as needed
            ).execute()
            start_page_token = changes.get('newStartPageToken')
            results.extend(changes['changes'])
            if not start_page_token:
                break
        except errors.HttpError as error:
            print(f"An error occurred: {error}")
            break
    return results, start_page_token

# Function to send an email
def send_email(recipient, message):
    # Replace with your email server and credentials
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'docsalertbot@gmail.com'
    smtp_password = 'Alertbot89'

    from_email = 'docs-alert-bot@gmail.com'

    rec_email = None

    #LOGIC FOR SUBJECT
    if recipient == 'Jason':
        rec_email = 'EagleEyeJZ1234@gmail.com'
        subject = 'Felix is on n3x'
    elif recipient == 'Felix':
        rec_email = 'tongfelix000@gmail.com'
        subject = 'Jason is on n3x'
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, rec_email, text)
        server.quit()
        print(f"Email sent to {recipient} with subject: {subject}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Create a service account credentials object
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Create a Google Drive API client
drive_service = build('drive', 'v3', credentials=credentials)

# Replace with the ID of the Google Docs document you want to monitor
document_id = '1bpqrUGo8mqUH5Tb7bcdbn41m_OHCLHw-eFG6IXBFeEA'

# Get the current start page token
response = drive_service.changes().getStartPageToken().execute()
start_page_token = response.get('startPageToken')

while True:
    changes, start_page_token = list_recent_changes(drive_service, document_id, start_page_token)
    for change in changes:
        if 'file' in change and 'id' in change['file'] and change['file']['id'] == document_id:
            # A change has occurred in the specified document
            text = change.get('file').get('name')
            if text:
                # Define a regular expression pattern to match the !alert (person) command
                pattern = r'!alert \((.*?)\)'
                matches = re.findall(pattern, text)
                if matches:
                    # Extract the person's name from the command
                    person = matches[0]
                    # Send an email to the specified person
                    send_email(person, f'Subject')

    # Poll for changes every 60 seconds (adjust as needed)
    time.sleep(60)
