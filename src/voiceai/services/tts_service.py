import asyncio
from elevenlabs.client import AsyncElevenLabs
from voiceai import config
import sounddevice as sd
import numpy as np

class ElevenLabsTTSService:
    """Text-to-speech via ElevenLabs streaming API."""

    def __init__(self):
        self.api_key = config.ELEVENLABS_API_KEY
        self.voice_id = config.ELEVENLABS_VOICE_ID
        self.model_id = config.ELEVENLABS_MODEL_ID
        self.client = AsyncElevenLabs(api_key=self.api_key)
        self.greeting_audio_cache = None
        
    async def connect(self):
        try:
            return True
        except Exception as e:
            return False
    
    async def generate_greeting(self, greeting_text):
        if self.greeting_audio_cache is not None:
            return self.greeting_audio_cache
        
        try:
            audio_data = b""
            async for chunk in self.stream_text(greeting_text):
                audio_data += chunk
            
            self.greeting_audio_cache = audio_data
            return audio_data
        except Exception as e:
            return None
    
    async def stream_text(self, text):
        try:
            audio_stream = self.client.text_to_speech.convert_as_stream(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                output_format="pcm_16000"
            )
            
            chunk_count = 0
            async for chunk in audio_stream:
                if chunk:
                    chunk_count += 1
                    yield chunk
            
            if chunk_count == 0:
                print("Warning: ElevenLabs returned 0 audio chunks")
                    
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            yield b""
    
    async def speak_text(self, text):
        try:
            audio_chunks = []
            async for chunk in self.stream_text(text):
                if chunk:
                    audio_chunks.append(chunk)
            
            if audio_chunks:
                full_audio = b"".join(audio_chunks)
                if len(full_audio) > 0:
                    await self._play_audio(full_audio, sample_rate=16000)
                else:
                    print("Warning: No audio data generated")
                
        except Exception as e:
            print(f"TTS speak error: {e}")
    
    async def _play_audio(self, audio_data, sample_rate=16000):
        try:
            if len(audio_data) == 0:
                return
                
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            sd.play(audio_array, samplerate=sample_rate, blocking=False)
            sd.wait()
                
        except Exception as e:
            print(f"Audio playback error: {e}")
    
    def play_audio_sync(self, audio_data, sample_rate=16000):
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            sd.play(audio_array, samplerate=sample_rate)
            sd.wait()
        except Exception as e:
            pass

