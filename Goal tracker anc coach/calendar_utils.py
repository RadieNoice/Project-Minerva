import datetime
import os.path
import pickle
from typing import Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def authenticate_google_calendar():
    """Authenticate and return Google Calendar service."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service

def create_events_from_plan(service, habit_plan: Dict[str, List[Dict[str, str]]], start_date: datetime.date):
    """Push each daily task with time as an event into Google Calendar."""
    for week_index, (week, tasks) in enumerate(habit_plan.items()):
        for task in tasks:
            task_time = task["time"]
            task_desc = task["task"]

            try:
                # Parse time string into hour and minute
                time_obj = datetime.datetime.strptime(task_time, "%I:%M %p")
                hour, minute = time_obj.hour, time_obj.minute
            except ValueError:
                print(f"Invalid time format for task: {task}")
                continue

            # Spread tasks over weekdays in the current week
            for day_offset in range(5):  # Mon–Fri
                day = start_date + datetime.timedelta(weeks=week_index, days=day_offset)
                start_dt = datetime.datetime.combine(day, datetime.time(hour, minute))
                end_dt = start_dt + datetime.timedelta(minutes=30)

                event = {
                    "summary": task_desc,
                    "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"},
                }

                service.events().insert(calendarId="primary", body=event).execute()
