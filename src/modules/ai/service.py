import logging
from .llm import LLM
from .stt import STT
from .tts import TTS

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, on_response: callable):
        self._on_response = on_response
        self.llm = LLM(on_generate=self._handle_llm_response)
        self.stt = STT(on_transcript=self._handle_transcript)
        self.tts = TTS(on_speach=self._handle_speech)


    async def handle_audio_status(self, audio_content):
        # Treat 'SPEAKING' as the user is actively sending audio
        if audio_content.status == "SPEAKING":
            if not self.stt.status:
                await self.stt.start_listening()
            if getattr(audio_content, "audio", None):
                import base64
                audio_data = base64.b64decode(audio_content.audio)
                self.stt.transcribe_audio(audio_data)
        elif audio_content.status == "STOPPED":
            if self.stt.status:
                await self.stt.stop_listening()

    def _handle_transcript(self, text):
        logger.info(f"Transcript: {text}")
        self._on_response("TRANSCRIPT", text)

        response = self.llm.handle_input(text)
        if response:
            self._on_response("TEXT", response)
            self.tts.speak(response)

    def _handle_llm_response(self, response):
        self.tts.speak(response)

    def _handle_speech(self, audio_data):
        self._on_response("AUDIO", audio_data)