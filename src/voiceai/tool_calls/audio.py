from typing import Optional
from src.voiceai.services.audio_handler import AudioHandler


class _AudioTools:
    def __init__(self):
        self._svc = AudioHandler()

    def start(self):
        return self._svc.start_recording()

    def read_chunk(self) -> Optional[bytes]:
        return self._svc.read_audio_chunk()

    def stop(self):
        self._svc.stop_recording()

    def cleanup(self):
        self._svc.cleanup()


audio = _AudioTools()


