import json
import base64
from .schemas import AudioInputMessage, AudioStatus
from src.extensions import STTClient,  AIClient #, TTSClient

# Note: TTSClient is not used in this service but will be added later for text-to-speech functionality.
# Text-to-speech will be implemented and the audio will be sent to the output WebSocket to be played by the client.   

class CommunicationService:
    def __init__(self):
        self.client_stream = None
        self.server_stream = None
        
        self.ai = AIClient()
        self.stt = STTClient(on_transcript=self.on_transcript)
        
    def register_client_stream(self, websocket):
        self.input_ws = websocket
        
    def register_server_stream(self, websocket):
        self.server_stream = websocket
        
    async def process_audio_message(self, raw_message):
        if not self.input_ws:
            print("[CommunicationService] No input WebSocket registered.")
            return
        
        try:
            message = json.loads(raw_message)
            
            try:
                message = AudioInputMessage(**message)
            except Exception as e:
                print("[CommunicationService] Invalid message format:", e)
                await self.server_stream.send(json.dumps({"error": "Invalid input message format"}))
                return
            
            if message.status == AudioStatus.LISTENING:
                if not self.stt.status:
                    await self.stt.start_listening()
                    print("[CommunicationService] STT client started listening")
                if message.audio:
                    audio_data = base64.b64decode(message.audio)
                    self.stt.transcribe_audio(audio_data)
                    
            elif message.status == AudioStatus.STOPPED:
                if self.stt.status:
                    await self.stt.stop_listening()
                    print("[CommunicationService] STT client stopped listening")
                    
        except Exception as e:
            print("[CommunicationService] Error processing audio message:", e)
            
    async def on_transcript(self, text):
        if not self.server_stream:
            print("[CommunicationService] No output WebSocket registered.")
            return
        
        try:
            ai_response = await self.ai.send_message(text)
            print(f"[CommunicationService] AI response: {ai_response}")
        except Exception as e:
            print("[CommunicationService] WebSocket send error:", e)
        

communication_service = CommunicationService()