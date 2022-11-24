from __future__ import print_function
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

app = FastAPI()

origins = [
    "https://localhost:3010",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.get("/calendar")
def read_root():
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow()
    timeMin = now.replace(hour=0, minute=0, second=0, microsecond=0)
    timeMax = now.replace(hour=23, minute=59, second=59, microsecond=0)
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=timeMin.isoformat() + 'Z', timeMax=timeMax.isoformat() + 'Z', singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    response_data = []
    if not events:
        print('No upcoming events found.')
        return response_data
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        response_data.append({
            'start_time': start,
            'title': event['summary']
        })
        print(start, event['summary'])

    return response_data