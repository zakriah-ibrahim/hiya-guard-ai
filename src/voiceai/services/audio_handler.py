import pyaudio
import webrtcvad
import sounddevice as sd
import numpy as np
import asyncio
from collections import deque
from voiceai import config

class AudioHandler:
    """Microphone capture, simple Voice Activity Detection, and playback helpers."""

    def __init__(self):
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.channels = config.AUDIO_CHANNELS
        self.chunk_size = config.AUDIO_CHUNK_SIZE
        self.format = pyaudio.paInt16
        
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None
        self.vad = webrtcvad.Vad(config.VAD_AGGRESSIVENESS)
        
        self.is_recording = False
        self.audio_buffer = deque(maxlen=50)
        
        self.frame_duration_ms = config.VAD_FRAME_DURATION_MS
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        
    def start_recording(self):
        try:
            self.is_recording = True
            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=None
            )
            print(f"Audio stream created: {self.sample_rate}Hz, {self.channels} channel(s)")
            return self.stream
        except Exception as e:
            print(f"Failed to create audio stream: {e}")
            return None
    
    def read_audio_chunk(self):
        if self.stream and self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                if len(data) > 0:
                    return data
                else:
                    return None
            except Exception as e:
                return None
        return None
    
    def apply_vad(self, audio_data):
        if len(audio_data) != self.frame_size * 2:
            return False
        
        try:
            is_speech = self.vad.is_speech(audio_data, self.sample_rate)
            return is_speech
        except Exception as e:
            return False
    
    def buffer_audio(self, audio_data):
        self.audio_buffer.append(audio_data)
    
    def get_buffered_audio(self):
        buffered = b''.join(self.audio_buffer)
        self.audio_buffer.clear()
        return buffered
    
    def play_audio(self, audio_data, sample_rate=None):
        if sample_rate is None:
            sample_rate = self.sample_rate
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            sd.play(audio_array, samplerate=sample_rate)
            sd.wait()
        except Exception as e:
            pass
    
    async def play_audio_async(self, audio_data, sample_rate=None):
        if sample_rate is None:
            sample_rate = self.sample_rate
        
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            sd.play(audio_array, samplerate=sample_rate)
            
            while sd.get_stream().active:
                await asyncio.sleep(0.01)
        except Exception as e:
            pass
    
    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def cleanup(self):
        self.stop_recording()
        self.pyaudio_instance.terminate()

