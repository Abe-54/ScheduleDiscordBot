import datetime
import os
from typing import Optional
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

def is_calandar_connected():
    return os.path.exists("token.json")

def add_event_to_new_calendar(user_id: int, description: str, start_time: datetime, end_time: datetime, calendar: Optional[dict] = None):
    
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    if calendar is None:
        calendar = {
            'summary' : 'Work Schedule Calendar',
            'timeZone' : 'America/New_York'
        }
        
        new_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = new_calendar["id"]
        print(f"Created calendar: {calendar_id}")
    else:
        calendar_id = calendar["id"]
    
    shift = {
        "summary": "Work Shift",
        "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "America/New_York"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "America/New_York"},
    }
    
    event = (
        service.events().insert(calendarId=calendar_id, body=shift).execute()
    )   

    return event
