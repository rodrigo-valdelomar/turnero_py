from __future__ import print_function

from django.shortcuts import render

from datetime import datetime, timedelta
import os.path

import json
import ast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.http import HttpResponse

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# class Appointment:
#     def __init__(self, date, time, name, email, description):
#         self.date = date
#         self.time = time
#         self.name = name
#         self.email = email
#         self.description = description

def availableDate(request):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        # print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=100, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        turnos_ocupados = []
        date = []

        if not events:
            print('No upcoming events found.')
            return
        
        # Prints the start and name of the next 10 events
        for event in events:
            if event["summary"] == "Apertura":
                start = event["start"].get('dateTime', event['start'].get('date'))
                aux = start.split("-")
                date.append(aux[2][0:2]+"/"+aux[1])

        return date[0:5]

    except:
        date = "Sin fechas disponibles"


def availableAppointment(request, min, max):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        events_result = service.events().list(calendarId='primary', timeMin=min, timeMax=max,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        turnos_ocupados = []

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            if event["summary"] == "Apertura":
                apertura_gral = event["start"].get('dateTime', event['start'].get('date'))
            elif str.lower(event["summary"]) == "cierre":
                cierre_gral = event["start"].get('dateTime', event['start'].get('date'))
            else:
                start = event['start'].get('dateTime', event['start'].get('date'))
                evento_gral = start.split("T")
                evento_gral = evento_gral[1].split("-")
                turnos_ocupados.append(evento_gral[0][0:5])
        
        apertura_gral = apertura_gral.split("T")
        apertura_gral = apertura_gral[1].split("-")
        apertura = apertura_gral[0].split(":")

        cierre_gral = cierre_gral.split("T")
        cierre_gral = cierre_gral[1].split("-")
        cierre = cierre_gral[0].split(":")

        if apertura[1] != cierre[1] and apertura[1] > cierre[1]:
            cierre[1] += 60
            cierre[0] -= 1
            
        horas_apertura = int(cierre[0]) - int(apertura[0])

        turnos_posibles = []

        for i in range(horas_apertura):
            turnos_posibles.append(str((int(apertura[0]) + i)) + ":" + apertura[1])

        for turno in turnos_ocupados:
            try:
                turnos_posibles.remove(turno)
            except:
                pass

        return(turnos_posibles)

    except HttpError as error:
        print('An error occurred: %s' % error)

def createAppointment(request, name, mail, start, end, tratamiento):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        description = "Turno de: "+tratamiento+" para: "+name

        # Call the Calendar API
        event = {
        'summary': tratamiento,
        'location': 'https://g.page/Leadaki?share',
        'description': description,
        'start': {
            'dateTime': start,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
            'dateTime': end,
            'timeZone': 'America/Argentina/Buenos_Aires',
        },
        # 'recurrence': [
        #     'RRULE:FREQ=DAILY;COUNT=1'
        # ],
        'attendees': [
            {'email': mail        }],
        "conferenceData": [
            {"createRequest": True}
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
            ],
        },
        }

        new_event = service.events().insert(calendarId = "primary", body=event).execute()
        # print("Evento creado en: %s" % (event.get("htmlLink")))

        return

    except:
        print("no funcionó")

def prueba_recepcion(request):
    if request.method == "POST":
        data = request.body

        dict_str = data.decode("UTF-8")
        mydata = json.loads(dict_str)
        email = mydata["collected_data"]["email"]
        
        print("Raw data:", mydata)

        mensaje = {
            "name": {
                "value": "Juan Roman",
            },
            "email": {
                "value": "juanroman@diez.com"
            },
            "phone": {
                "national_format": "1234542123",
                "international_format": "12343132112"
            },
            "custom": { 
                "userType": "advanced",
                "thing1": "something",
                "thing2": "something"
            },
            "response": {
                "text": ['que día queres el turno'],
                "response_type": 'LIST',
                "response_options": ["una", "dos"],
                "stopChat": "true",
                "flow": "5"
            }
        }
    return HttpResponse("hizo la consulta")