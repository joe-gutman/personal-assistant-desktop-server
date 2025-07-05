import json
import base64
import logging
from .schemas import AudioInputMessage, AudioStatus
from src.extensions import STTClient, AIClient  # , TTSClient

logger = logging.getLogger(__name__)

# Note: TTSClient is not used in this service but will be added later for text-to-speech functionality.

class CommunicationService:
    def __init__(self):
        self.client_stream = None
        self.server_stream = None

        self.ai = AIClient()
        
        self.stt = STTClient(on_transcript=self.on_transcript)

        logger.debug("CommunicationService initialized.")

    def register_client_stream(self, websocket):
        self.input_ws = websocket

    def register_server_stream(self, websocket):
        self.server_stream = websocket

    async def process_audio_message(self, raw_message):
        if not self.input_ws:
            logger.warning("No input WebSocket registered.")
            return

        try:
            message = json.loads(raw_message)

            try:
                message = AudioInputMessage(**message)
            except Exception as e:
                logger.error(f"Invalid message format: {e}", exc_info=True)
                await self.server_stream.send(json.dumps({"error": "Invalid input message format"}))
                return

            if message.status == AudioStatus.LISTENING:
                if not self.stt.status:
                    await self.stt.start_listening()
                if message.audio:
                    audio_data = base64.b64decode(message.audio)
                    self.stt.transcribe_audio(audio_data)

            elif message.status == AudioStatus.STOPPED:
                if self.stt.status:
                    await self.stt.stop_listening()

        except Exception as e:
            logger.error(f"Error processing audio message: {e}", exc_info=True)

    async def on_transcript(self, text):
        if not self.server_stream:
            logger.warning("No output WebSocket registered.")
            return

        try:
            ai_response = self.ai.handle_user_input(text)
            logger.info(f"AI response: {ai_response}")
        except Exception as e:
            logger.error(f"WebSocket send error: {e}", exc_info=True)


communication_service = CommunicationService()
