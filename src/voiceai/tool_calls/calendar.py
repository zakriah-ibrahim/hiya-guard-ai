from datetime import datetime
from src.voiceai.services.calendar_service import GoogleCalendarService


class _CalendarTools:
    def __init__(self):
        self._svc = GoogleCalendarService()
        self._authed = False

    def authenticate(self):
        if not self._authed:
            self._authed = bool(self._svc.authenticate())
        return self._authed

    def get_free_slots(self, days_ahead: int = 3, slot_duration_minutes: int = 30):
        if not self._authed:
            self.authenticate()
        return self._svc.get_free_slots(days_ahead=days_ahead, slot_duration_minutes=slot_duration_minutes)

    def create_event(self, start_time: datetime, purpose: str, info: str = ""):
        if not self._authed:
            self.authenticate()
        return self._svc.create_event(start_time, purpose, info)

    def format_slots(self, slots):
        return self._svc.format_time_slots(slots)


calendar = _CalendarTools()


