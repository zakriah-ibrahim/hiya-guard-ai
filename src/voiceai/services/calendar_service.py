import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    """Google Calendar operations: auth, free slot search, event creation."""

    def __init__(self):
        self.service = None
        self.calendar_id = 'primary'
        
    def authenticate(self):
        creds = None
        
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def get_free_slots(self, days_ahead: int = 3, slot_duration_minutes: int = 30):
        try:
            # Use local timezone-aware datetimes to avoid naive/aware comparison issues
            now = datetime.now().astimezone()
            end_time = now + timedelta(days=days_ahead)
            
            body = {
                "timeMin": now.isoformat(),
                "timeMax": end_time.isoformat(),
                "items": [{"id": self.calendar_id}],
                "timeZone": "America/New_York"
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            busy_times = freebusy_result['calendars'][self.calendar_id]['busy']
            
            print(f"Freebusy query returned {len(busy_times)} busy periods")
            if busy_times:
                print("Busy periods:")
                for i, busy in enumerate(busy_times[:3]):  # Show first 3
                    print(f"  {i+1}. {busy['start']} to {busy['end']}")
            
            # Also get existing events to double-check
            existing_events = self._get_existing_events(now, end_time)
            
            free_slots = self._find_free_slots(
                now, end_time, busy_times, slot_duration_minutes, existing_events
            )
            
            return free_slots[:5]
            
        except Exception as e:
            print(f"Calendar freebusy query error: {e}")
            return self._get_fallback_slots()
    
    def _get_existing_events(self, start_time, end_time):
        """Get existing events for the time period."""
        try:
            # Use RFC3339 aware datetimes directly (includes offset)
            aware_start = start_time if start_time.tzinfo else start_time.astimezone()
            aware_end = end_time if end_time.tzinfo else end_time.astimezone()
            time_min = aware_start.isoformat()
            time_max = aware_end.isoformat()
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"Found {len(events)} existing events in calendar")
            return events
            
        except Exception as e:
            print(f"Error fetching existing events: {e}")
            return []
    
    def _find_free_slots(self, start_time, end_time, busy_times, slot_duration_minutes, existing_events=None):
        free_slots = []
        current = start_time if start_time.tzinfo else start_time.astimezone()
        
        business_hours_start = 9
        business_hours_end = 17
        
        # Ensure we start from tomorrow if today is too late
        if current.hour >= business_hours_end:
            current = (current + timedelta(days=1)).replace(
                hour=business_hours_start, minute=0, second=0, microsecond=0
            )
        
        while current < end_time and len(free_slots) < 10:
            current_hour = current.hour
            
            # Skip if before business hours
            if current_hour < business_hours_start:
                current = current.replace(hour=business_hours_start, minute=0, second=0, microsecond=0)
                continue
            
            # Skip if after business hours
            if current_hour >= business_hours_end:
                current = (current + timedelta(days=1)).replace(
                    hour=business_hours_start, minute=0, second=0, microsecond=0
                )
                continue
            
            # Skip weekends
            if current.weekday() >= 5:
                current = (current + timedelta(days=1)).replace(
                    hour=business_hours_start, minute=0, second=0, microsecond=0
                )
                continue
            
            slot_end = current + timedelta(minutes=slot_duration_minutes)
            
            # Check if slot conflicts with busy times
            is_free = True
            
            # Check freebusy results
            for busy in busy_times:
                try:
                    # Handle different timezone formats
                    busy_start_str = busy['start']
                    busy_end_str = busy['end']
                    
                    # Parse busy times with timezone handling
                    if busy_start_str.endswith('Z'):
                        busy_start = datetime.fromisoformat(busy_start_str.replace('Z', '+00:00'))
                    else:
                        busy_start = datetime.fromisoformat(busy_start_str)
                    
                    if busy_end_str.endswith('Z'):
                        busy_end = datetime.fromisoformat(busy_end_str.replace('Z', '+00:00'))
                    else:
                        busy_end = datetime.fromisoformat(busy_end_str)
                    
                    # Check for overlap
                    if (current < busy_end and slot_end > busy_start):
                        is_free = False
                        current = busy_end
                        break
                except Exception as e:
                    # Skip malformed busy times
                    continue
            
            # Double-check with existing events if provided
            if is_free and existing_events:
                for event in existing_events:
                    try:
                        start_field = event['start']
                        end_field = event['end']
                        event_start = start_field.get('dateTime') or start_field.get('date')
                        event_end = end_field.get('dateTime') or end_field.get('date')
                        
                        if event_start and event_end:
                            # Handle all-day events (date only) vs dateTime
                            if len(event_start) == 10:  # 'YYYY-MM-DD'
                                # All-day event: spans from 00:00 local time to next day 00:00
                                day_start = datetime.fromisoformat(event_start).astimezone(current.tzinfo)
                                day_end = datetime.fromisoformat(event_end).astimezone(current.tzinfo)
                                event_start_dt = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
                                event_end_dt = day_end.replace(hour=0, minute=0, second=0, microsecond=0)
                            else:
                                # Parse event times with timezone handling
                                if event_start.endswith('Z'):
                                    event_start_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
                                else:
                                    event_start_dt = datetime.fromisoformat(event_start)
                                if event_end.endswith('Z'):
                                    event_end_dt = datetime.fromisoformat(event_end.replace('Z', '+00:00'))
                                else:
                                    event_end_dt = datetime.fromisoformat(event_end)
                            
                            # Check for overlap (with some tolerance for timezone differences)
                            if (current < event_end_dt and slot_end > event_start_dt):
                                print(f"  Slot {current} conflicts with event: {event.get('summary', 'Untitled')} ({event_start} - {event_end})")
                                is_free = False
                                current = event_end_dt
                                break
                    except Exception as e:
                        # Skip malformed events
                        print(f"  Skipping malformed event: {e}")
                        continue
            
            if is_free:
                free_slots.append(current)
                current = slot_end
            else:
                # Move to next 30-minute slot
                current = current.replace(minute=((current.minute // 30) + 1) * 30)
                if current.minute >= 60:
                    current = current.replace(hour=current.hour + 1, minute=0)
        
        return free_slots
    
    def _get_fallback_slots(self):
        now = datetime.now()
        fallback_slots = []
        
        for i in range(1, 4):
            day = now + timedelta(days=i)
            if day.weekday() < 5:
                slot1 = day.replace(hour=10, minute=0, second=0, microsecond=0)
                slot2 = day.replace(hour=14, minute=0, second=0, microsecond=0)
                fallback_slots.extend([slot1, slot2])
        
        return fallback_slots[:5]
    
    def format_time_slots(self, slots):
        formatted = []
        for slot in slots:
            day_name = slot.strftime("%A")
            time_str = slot.strftime("%I:%M %p")
            formatted.append(f"{day_name} at {time_str}")
        
        return formatted
    
    def create_event(self, start_time, caller_purpose, caller_info=""):
        try:
            end_time = start_time + timedelta(minutes=30)
            
            # Use local timezone for event creation
            event = {
                'summary': f'Callback: {caller_purpose}',
                'description': f'Scheduled callback.\n\nCaller Info: {caller_info}',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return created_event.get('htmlLink')
            
        except Exception as e:
            print(f"Calendar event creation error: {e}")
            return None

