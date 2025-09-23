import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import Request

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials():
    """
    Authenticate with Google and return creds object.
    Only for MVP -> one local user (you).
    """
    token_path = "tokens/token.json"

    # Load saved token if exists
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no valid creds, force browser login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # auto refresh
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)  # opens browser
        # Save for next time
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds


def test_calendar_connection():
    """
    Simple test to validate we can call Google Calendar API.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    calendars = service.calendarList().list().execute()

    return [cal["summary"] for cal in calendars.get("items", [])]