import json
import base64
from src.extensions import STTClient,  AIClient #, TTSClient

# Note: TTSClient is not used in this service but will be added later for text-to-speech functionality.
# Text-to-speech will be implemented and the audio will be sent to the output WebSocket to be played by the client.   

class CommunicationService:
    def __init__(self):
        self.input_ws = None
        self.output_ws = None
        
        self.ai = AIClient()
        self.stt = STTClient(on_transcript=self.on_transcript)
        
    def register_input_socket(self, websocket):
        self.input_ws = websocket
        
    def register_output_socket(self, websocket):
        self.output_ws = websocket
        
    async def process_audio_message(self, message):
        if not self.input_ws:
            print("[CommunicationService] No input WebSocket registered.")
            return
        
        try:
            message = json.loads(message)
            status = message.get('status')
            audio_data = message.get('audio')
            
            if status == "LISTENING":
                if not self.stt.status:
                    await self.stt.start_listening()
                    print("[CommunicationService] STT client started listening")
                if audio_data:
                    audio_data = base64.b64decode(audio_data)
                    self.stt.transcribe_audio(audio_data)
                    
            elif status == "STOPPED":
                if self.stt.status:
                    await self.stt.stop_listening()
                    print("[CommunicationService] STT client stopped listening")
                    
        except Exception as e:
            print("[CommunicationService] Error processing audio message:", e)
            
    async def on_transcript(self, text):
        if not self.output_ws:
            print("[CommunicationService] No output WebSocket registered.")
            return
        
        try:
            ai_response = await self.ai.send_message(text)
            print(f"[CommunicationService] AI response: {ai_response}")
        except Exception as e:
            print("[CommunicationService] WebSocket send error:", e)
        

communication_service = CommunicationService()