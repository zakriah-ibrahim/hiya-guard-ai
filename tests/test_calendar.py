import asyncio
from src.voiceai.services.calendar_service import GoogleCalendarService
from datetime import datetime

async def test_calendar():
    print("="*60)
    print("Google Calendar Test - Current Date Verification")
    print("="*60)
    
    print(f"Current system date: {datetime.now()}")
    print(f"Current system date (ISO): {datetime.now().isoformat()}")
    
    try:
        calendar = GoogleCalendarService()
        print("\n1. Authenticating with Google Calendar...")
        calendar.authenticate()
        print("Authentication successful")
        
        print("\n2. Getting free slots for next 3 days...")
        free_slots = calendar.get_free_slots(days_ahead=3, slot_duration_minutes=30)
        
        if free_slots:
            print(f"Found {len(free_slots)} free slots:")
            formatted_slots = calendar.format_time_slots(free_slots)
            for i, slot in enumerate(formatted_slots, 1):
                print(f"  {i}. {slot}")
                print(f"     Raw datetime: {free_slots[i-1]}")
        else:
            print("No free slots found")
        
        print("\n3. Testing event creation...")
        if free_slots:
            test_time = free_slots[0]
            print(f"Creating test event for: {test_time}")
            
            event_link = calendar.create_event(
                test_time,
                "Test Callback - Blood Test Discussion",
                "Dr. Sunil - 347-8FLY-7765"
            )
            
            if event_link:
                print(f"Event created successfully: {event_link}")
            else:
                print("Event creation failed")
        
    except Exception as e:
        print(f"Calendar test failed: {e}")
    
    print("\n" + "="*60)
    print("Calendar test complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_calendar())
