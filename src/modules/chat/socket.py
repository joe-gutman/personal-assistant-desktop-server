from quart import websocket, Blueprint

chat_socket_bp = Blueprint("chat_socket", __name__)

@chat_socket_bp.websocket("/ws/chat")
async def chat_ws():
    print("WebSocket connected: CHAT")
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive()
            print(f"[Chat] Received: {data}")
            await websocket.send(data)
    except Exception as e:
        print("Chat socket error:", e)
        await websocket.close()
