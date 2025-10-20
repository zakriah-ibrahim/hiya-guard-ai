from typing import Callable, Optional
from src.voiceai.services.stt_service import AssemblyAISTTService


class _STTTools:
    def __init__(self):
        self._svc: Optional[AssemblyAISTTService] = None

    def init(self, on_transcript: Callable[[str, bool], None]):
        self._svc = AssemblyAISTTService(on_transcript)

    async def connect(self):
        if not self._svc:
            raise RuntimeError("STT not initialized. Call init(on_transcript) first.")
        return await self._svc.connect()

    async def start(self):
        if not self._svc:
            raise RuntimeError("STT not initialized. Call init(on_transcript) first.")
        return await self._svc.start_streaming()

    async def stream_audio(self, audio: bytes):
        if not self._svc:
            return
        await self._svc.stream_audio(audio)

    async def disconnect(self):
        if self._svc:
            await self._svc.disconnect()


stt = _STTTools()


