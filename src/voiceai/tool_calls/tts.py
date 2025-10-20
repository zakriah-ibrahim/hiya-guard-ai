from src.voiceai.services.tts_service import ElevenLabsTTSService


class _TTSTools:
    def __init__(self):
        self._svc = ElevenLabsTTSService()
        self._connected = False

    async def connect(self):
        if not self._connected:
            self._connected = bool(await self._svc.connect())
        return self._connected

    async def generate_greeting(self, text: str):
        if not self._connected:
            await self.connect()
        return await self._svc.generate_greeting(text)

    async def speak(self, text: str):
        if not self._connected:
            await self.connect()
        await self._svc.speak_text(text)


tts = _TTSTools()


