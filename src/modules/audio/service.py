import json
import asyncio
import base64
from src.extensions import STTClient

async def handle_audio_stream(websocket):
    print("WebSocket connected: AUDIO")
    await websocket.accept()

    # Define the transcript callback
    async def on_transcript(text):
        try:
            await websocket.send(text)
        except Exception as e:
            print("[Audio] WebSocket send error:", e)

    # Initialize the STT client with the callback
    stt_client = STTClient(on_transcript=on_transcript, chunk_seconds=8)
    transcribe_task = None

    try:
        while True:
            message = json.loads(await websocket.receive())
            status = message.get('status')
            audio_data = message.get('audio')
            if (status == "LISTENING"):
                if not await stt_client.get_status():
                    await stt_client.start_listening()
                    print("[Audio] STT client started listening")
                if audio_data:
                    audio_data = base64.b64decode(message.get('audio'))
                    stt_client.transcribe_audio(audio_data)
            elif (status == "STOPPED"): 
                if stt_client.get_status():
                    await stt_client.stop_listening()
                    print("[Audio] STT client stopped listening")
            # print(f"[Audio] Received data: [{data[:5]}]...")
    except Exception as e:
        print("[Audio] Stream error:", e)
    finally:
        stt_client.stop()
        await websocket.close(code=1000, reason="[Audio] Stream closed")
