from quart import websocket, Blueprint
import json

audio_socket_bp = Blueprint('audio_socket', __name__)

@audio_socket_bp.websocket('/ws/audio')
async def audio_ws():
    print("WebSocket connected for audio")
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive()
            print(f"Received: {len(data)} bytes")
            response = {"status": "received", "length": len(data)}
            await websocket.send_json(response)
    except Exception as e:
        print("WebSocket connection closed:", str(e))
        await websocket.close()