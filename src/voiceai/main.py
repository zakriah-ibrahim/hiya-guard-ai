import asyncio
import sys
from datetime import datetime
from src.voiceai.services.audio_handler import AudioHandler
from src.voiceai.services.stt_service import AssemblyAISTTService
from src.voiceai.services.llm_service import ConversationEngine
from src.voiceai.services.tts_service import ElevenLabsTTSService
from src.voiceai.services.calendar_service import GoogleCalendarService
from src.voiceai import config

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class VoiceGuardAI:
    def __init__(self):
        self.audio_handler = AudioHandler()
        self.llm_engine = ConversationEngine()
        self.tts_service = ElevenLabsTTSService()
        self.calendar_service = GoogleCalendarService()
        
        self.stt_service = None
        self.is_call_active = False
        self.full_transcript = []
        self.silence_counter = 0
        self.last_speech_time = None
        
        self.pending_action = None
        self.scheduled_time = None
        self.caller_purpose = ""
        self.available_slots = []
        self.confirmation_received = False
        
    async def initialize(self):
        print("Initializing Hiya Guard...")
        
        try:
            self.calendar_service.authenticate()
            print("Google Calendar authenticated")
        except Exception as e:
            print(f"Calendar authentication failed: {e}")
            print("  Continuing without calendar integration")
        
        await self.tts_service.connect()
        
        greeting_text = f"Hello, you've reached {config.USER_NAME}'s AI assistant. How can I help you?"
        print("Generating greeting audio...")
        greeting_audio = await self.tts_service.generate_greeting(greeting_text)
        
        self.llm_engine.initialize_conversation()
        
        print("Hiya Guard ready")
        print("\nPress Enter to answer incoming call...")
    
    async def on_transcript(self, transcript, is_final):
        if is_final:
            print(f"\nCaller: {transcript}")
            self.full_transcript.append(f"Caller: {transcript}")
            
            response_data = await self.llm_engine.process_transcript(transcript)
            
            agent_response = response_data.get("response", "")
            intent = response_data.get("intent", "unclear")
            action = response_data.get("action", "continue")
            confidence = response_data.get("confidence", 0.5)
            
            print(f"Agent: {agent_response}")
            self.full_transcript.append(f"Agent: {agent_response}")
            
            self.llm_engine.update_conversation_state(intent, confidence)
            
            if action == "schedule":
                # Extract caller purpose from transcript for calendar event
                self.caller_purpose = self._extract_caller_purpose(transcript)
                await self.handle_scheduling(agent_response)
            elif action == "decline" or action == "end_call":
                self.pending_action = action
                await self.tts_service.speak_text(agent_response)
                self.is_call_active = False
            elif action == "confirm":
                await self.handle_confirmation(agent_response)
            else:
                await self.tts_service.speak_text(agent_response)
            
            self.last_speech_time = datetime.now()
    
    async def handle_scheduling(self, agent_response):
        try:
            free_slots = self.calendar_service.get_free_slots()
            
            if free_slots:
                formatted_slots = self.calendar_service.format_time_slots(free_slots[:3])
                
                slots_text = ", ".join(formatted_slots[:2])
                scheduling_message = f"{agent_response} Available times are {slots_text}. Which works for you?"
                
                print(f"Agent (with calendar): {scheduling_message}")
                self.full_transcript.append(f"Agent: {scheduling_message}")
                
                await self.tts_service.speak_text(scheduling_message)
                
                # Store available slots for later use
                self.available_slots = free_slots[:3]
            else:
                await self.tts_service.speak_text(agent_response)
                
        except Exception as e:
            await self.tts_service.speak_text(agent_response)
    
    async def handle_confirmation(self, agent_response):
        """Handle when user confirms a time slot"""
        try:
            if self.available_slots and not self.confirmation_received:
                # Parse user's requested time from the transcript
                user_requested_time = self._parse_user_time_request()
                
                if user_requested_time:
                    # Find the closest matching slot
                    self.scheduled_time = self._find_matching_slot(user_requested_time)
                else:
                    # Fallback to first available slot
                    self.scheduled_time = self.available_slots[0]
                
                self.confirmation_received = True
                
                # Create the calendar event immediately
                if self.scheduled_time:
                    event_link = self.calendar_service.create_event(
                        self.scheduled_time,
                        self.caller_purpose or "Callback Request",
                        "Scheduled via Hiya Guard"
                    )
                    
                    if event_link:
                        print(f"Calendar event created: {event_link}")
                
                confirmation_message = f"Perfect! I've scheduled your callback for {self.calendar_service.format_time_slots([self.scheduled_time])[0]}. Thank you for calling!"
                
                print(f"Agent (confirmed): {confirmation_message}")
                self.full_transcript.append(f"Agent: {confirmation_message}")
                
                await self.tts_service.speak_text(confirmation_message)
                
                # End the call after confirmation
                self.is_call_active = False
            else:
                await self.tts_service.speak_text(agent_response)
                
        except Exception as e:
            print(f"Confirmation error: {e}")
            await self.tts_service.speak_text(agent_response)
    
    def _parse_user_time_request(self):
        """Parse user's time request from the transcript"""
        if not self.full_transcript:
            return None
        
        # Get the last caller message
        last_caller_message = ""
        for message in reversed(self.full_transcript):
            if message.startswith("Caller:"):
                last_caller_message = message.replace("Caller:", "").strip().lower()
                break
        
        # Simple parsing for common time patterns
        import re
        
        # Look for day patterns
        day_patterns = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4,
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4
        }
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}):?(\d{0,2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):(\d{2})',
        ]
        
        requested_day = None
        requested_hour = None
        requested_minute = 0
        
        # Find day
        for day_name, day_num in day_patterns.items():
            if day_name in last_caller_message:
                requested_day = day_num
                break
        
        # Find time
        for pattern in time_patterns:
            match = re.search(pattern, last_caller_message)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    hour = int(groups[0])
                    if len(groups) > 2 and groups[2]:
                        ampm = groups[2].lower()
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                    elif len(groups) > 1 and groups[1]:
                        ampm = groups[1].lower()
                        if ampm == 'pm' and hour != 12:
                            hour += 12
                        elif ampm == 'am' and hour == 12:
                            hour = 0
                    
                    requested_hour = hour
                    if len(groups) > 1 and groups[1] and groups[1].isdigit():
                        requested_minute = int(groups[1])
                break
        
        if requested_day is not None and requested_hour is not None:
            from datetime import datetime, timedelta
            now = datetime.now()
            
            # Find the next occurrence of the requested day
            days_ahead = requested_day - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            target_date = now + timedelta(days=days_ahead)
            target_datetime = target_date.replace(
                hour=requested_hour, 
                minute=requested_minute, 
                second=0, 
                microsecond=0
            )
            
            return target_datetime
        
        return None
    
    def _find_matching_slot(self, requested_time):
        """Find the closest matching slot to the user's request"""
        if not self.available_slots or not requested_time:
            return self.available_slots[0] if self.available_slots else None
        
        # Find the slot closest to the requested time
        best_slot = None
        min_diff = float('inf')
        
        for slot in self.available_slots:
            diff = abs((slot - requested_time).total_seconds())
            if diff < min_diff:
                min_diff = diff
                best_slot = slot
        
        return best_slot or self.available_slots[0]
    
    def _extract_caller_purpose(self, transcript):
        """Extract the caller's purpose from the transcript"""
        # Simple extraction - look for common patterns
        purpose_keywords = [
            'blood test', 'appointment', 'meeting', 'call', 'callback',
            'discussion', 'consultation', 'follow up', 'check up'
        ]
        
        transcript_lower = transcript.lower()
        for keyword in purpose_keywords:
            if keyword in transcript_lower:
                return keyword.title()
        
        # Fallback to first few words
        words = transcript.split()[:3]
        return ' '.join(words) if words else "Callback Request"
    
    async def start_call(self):
        self.is_call_active = True
        self.full_transcript = []
        self.silence_counter = 0
        
        print("\n" + "="*60)
        print("CALL STARTED")
        print("="*60)
        
        greeting_text = f"Hello, you've reached {config.USER_NAME}'s AI assistant. How can I help you?"
        print(f"Agent: {greeting_text}")
        self.full_transcript.append(f"Agent: {greeting_text}")
        
        print("Playing greeting...")
        await self.tts_service.speak_text(greeting_text)
        print("Greeting complete. Listening for caller...")
        
        self.last_speech_time = datetime.now()
        
        self.stt_service = AssemblyAISTTService(self.on_transcript)
        connected = await self.stt_service.connect()
        
        if not connected:
            print("Warning: STT connection failed")
            return
        
        # Start AssemblyAI real-time streaming
        streaming_started = await self.stt_service.start_streaming()
        if not streaming_started:
            print("Warning: AssemblyAI streaming failed")
            return
        
        await self.conversation_loop()
    
    async def conversation_loop(self):
        print("Starting microphone recording...")
        stream = self.audio_handler.start_recording()
        
        if not stream:
            print("Failed to start microphone recording")
            self.is_call_active = False
            return
        
        print("Microphone recording started")
        
        audio_task = asyncio.create_task(self.stream_audio())
        monitor_task = asyncio.create_task(self.monitor_silence())
        
        await asyncio.gather(audio_task, monitor_task)
    
    async def stream_audio(self):
        audio_chunks_sent = 0
        while self.is_call_active:
            audio_data = self.audio_handler.read_audio_chunk()
            
            if audio_data and self.stt_service and self.stt_service.is_connected:
                await self.stt_service.stream_audio(audio_data)
                audio_chunks_sent += 1
                
                if audio_chunks_sent == 1:
                    print("Audio streaming to AssemblyAI started")
                elif audio_chunks_sent % 100 == 0:
                    print(f"  Sent {audio_chunks_sent} audio chunks to AssemblyAI")
            
            await asyncio.sleep(0.01)
    
    async def monitor_silence(self):
        while self.is_call_active:
            if self.last_speech_time:
                elapsed = (datetime.now() - self.last_speech_time).total_seconds()
                
                if elapsed > config.SILENCE_TIMEOUT_SECONDS:
                    print("\n[Silence detected - ending call]")
                    self.is_call_active = False
                    break
            
            await asyncio.sleep(1)
    
    async def end_call(self):
        print("\n" + "="*60)
        print("CALL ENDED")
        print("="*60)
        
        self.audio_handler.stop_recording()
        
        if self.stt_service:
            await self.stt_service.disconnect()
        
        print("\nGenerating call summary...")
        transcript_text = "\n".join(self.full_transcript)
        summary = await self.llm_engine.generate_summary(transcript_text)
        
        self.display_summary(summary)
    
    def display_summary(self, summary):
        print("\n" + "="*60)
        print("CALL SUMMARY")
        print("="*60)
        print(f"Caller Intent:     {summary.get('caller_intent', 'Unknown')}")
        print(f"Classification:    {summary.get('classification', 'Unknown')}")
        print(f"Outcome:           {summary.get('outcome', 'Unknown')}")
        print(f"Scheduled:         {summary.get('scheduled_callback', 'None')}")
        print(f"Key Details:       {summary.get('key_details', 'None')}")
        print(f"Confidence:        {summary.get('confidence_score', 0.0):.2f}")
        print("="*60)
    
    def cleanup(self):
        self.audio_handler.cleanup()

async def main():
    agent = VoiceGuardAI()
    
    try:
        await agent.initialize()
        
        input()
        
        await agent.start_call()
        
        await agent.end_call()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        agent.cleanup()
        print("\nHiya Guard shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())

