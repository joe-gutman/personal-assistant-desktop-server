from quart import websocket, Blueprint

audio_socket_bp = Blueprint("audio_socket", __name__)

@audio_socket_bp.websocket("/ws/audio")
async def audio_ws():
    print("WebSocket connected: audio")
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive()
            print(f"[Audio] Received: {data[:5]}")
            await websocket.send(data)
    except Exception as e:
        print("Audio socket error:", e)
        await websocket.close()