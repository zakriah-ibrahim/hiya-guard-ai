from src.voiceai.services.llm_service import ConversationEngine


class _LLMTools:
    def __init__(self):
        self._engine = ConversationEngine()
        self._initialized = False

    def initialize(self):
        if not self._initialized:
            self._engine.initialize_conversation()
            self._initialized = True

    async def process_transcript(self, transcript: str):
        if not self._initialized:
            self.initialize()
        return await self._engine.process_transcript(transcript)

    def update_state(self, intent: str, confidence: float):
        self._engine.update_conversation_state(intent, confidence)

    async def summarize(self, full_transcript: str):
        return await self._engine.generate_summary(full_transcript)


llm = _LLMTools()


