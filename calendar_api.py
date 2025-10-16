import datetime
import os
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pytz

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_credentials(force_refresh: bool = False):
    """
    Authenticate with Google and return creds object.
    Only for MVP -> one local user (you).
    """
    token_path = "tokens/token.json"
    client_secret_path = "credentials.json"
    creds = None

    os.makedirs(os.path.dirname(token_path), exist_ok=True)

    if os.path.exists(token_path):
        try:
            # Check if file is empty or just "{}"
            with open(token_path, "r") as f:
                content = f.read().strip()
                if not content or content == "{}":
                    raise ValueError("Token file is empty or blank JSON.")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception as e:
            print(f"Invalid or empty token file — regenerating ({e})")
            creds = None
    else:
        print("Token file not found — creating a new one.")
    
    if force_refresh:
        print("🔄 Forcing credentials refresh...")
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
        return creds

    # If there are no valid creds, force browser login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())  # auto refresh
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_path, SCOPES
            )
            creds = flow.run_local_server(port=0)  # opens browser
        # Save for next time
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds

def test_calendar_connection() -> bool:
    """
    Simple test to validate we can call the Google Calendar API.
    Returns True if connection is valid, False otherwise.
    """
    try:
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)
        calendars = service.calendarList().list().execute()

        print("Connection successful.")
        print("Calendars found:", [cal["summary"] for cal in calendars.get("items", [])])
        return True

    except Exception as e:
        print("Failed to connect to Google Calendar API.")
        print(f"Error: {e}")
        return False

def create_new_calendar(title: Optional[str] = "Work Schedule"):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    calendar = {
            'summary' : title,
            'timeZone' : 'America/New_York'
        }
    
    new_calendar = service.calendars().insert(body=calendar).execute()
    calendar_id = new_calendar["id"]
    print(f"Created calendar: {calendar_id}")

    return new_calendar

def get_primary_calendar():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    return service.calendars().get(calendarId="primary").execute()

def get_calendar_list():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    calendars = None

    try:
        calendars = service.calendarList().list().execute()
        print("Calendars found:", [cal["summary"] for cal in calendars.get("items", [])])
    
    except Exception as e:
        print("Failed to connect to Google Calendar API.")
        print(f"Error: {e}")
        return calendars

    return calendars.get("items", [])

def add_event_to_new_calendar(user_id: int, description: str, start_time: datetime, end_time: datetime, calendar_id: str):
    
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    
    shift = {
        "summary": "Work Shift",
        "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "America/New_York"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "America/New_York"},
    }

    # calendar_id = 'primary' if calendar is None else calendar[id]
    
    event = (
        service.events().insert(calendarId=calendar_id, body=shift).execute()
    )   

    return event

def get_events_between( calendar_id: str, time_min: datetime, time_max: datetime, tz_name: str = "America/New_York"):
    """Return events between two datetimes (inclusive) from a calendar."""
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)
    tz = pytz.timezone(tz_name)

    # Ensure both datetimes are localized
    if time_min.tzinfo is None:
        time_min = tz.localize(time_min)
    if time_max.tzinfo is None:
        time_max = tz.localize(time_max)

    events_result = (service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            timeZone="UTC",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])