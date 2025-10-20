import asyncio
import websockets
import json
from voiceai import config

class AssemblyAISTTService:
    """Real-time STT client for AssemblyAI Universal Streaming."""

    def __init__(self, on_transcript_callback):
        self.api_key = config.ASSEMBLYAI_API_KEY
        self.on_transcript_callback = on_transcript_callback
        self.websocket = None
        self.is_connected = False
        
    async def connect(self):
        try:
            print("Connecting to AssemblyAI Universal Streaming...")
            
            # Use the new Universal Streaming WebSocket endpoint
            uri = f"wss://streaming.assemblyai.com/v3/ws?sample_rate={config.AUDIO_SAMPLE_RATE}"
            headers = {"Authorization": self.api_key}
            
            self.websocket = await websockets.connect(uri, extra_headers=headers)
            self.is_connected = True
            
            print("AssemblyAI Universal Streaming WebSocket connected")
            
            # Start listening for responses in background
            asyncio.create_task(self._listen_for_responses())
            
            return True
        except Exception as e:
            print(f"AssemblyAI connection failed: {e}")
            self.is_connected = False
            return False
    
    async def _listen_for_responses(self):
        """Listen for transcription responses and forward them to the callback."""
        try:
            async for message in self.websocket:
                response = json.loads(message)
                
                if 'transcript' in response and response['transcript']:
                    transcript = response['transcript']
                    
                    # Check if this is end of turn
                    is_final = response.get('end_of_turn', False)
                    
                    await self.on_transcript_callback(transcript, is_final)
                    
        except websockets.exceptions.ConnectionClosed:
            print("[AssemblyAI] WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            print(f"[AssemblyAI] Response error: {e}")
            self.is_connected = False
    
    async def stream_audio(self, audio_data):
        if self.websocket and self.is_connected:
            try:
                # Send raw audio data directly to WebSocket
                await self.websocket.send(audio_data)
            except Exception as e:
                print(f"[AssemblyAI] Stream error: {e}")
                self.is_connected = False
    
    async def start_streaming(self):
        """Start the Universal Streaming connection"""
        if self.is_connected:
            print("AssemblyAI Universal Streaming ready")
            return True
        else:
            print("AssemblyAI not connected")
            return False
    
    async def disconnect(self):
        self.is_connected = False
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                print(f"[AssemblyAI] Disconnect error: {e}")
        self.websocket = None