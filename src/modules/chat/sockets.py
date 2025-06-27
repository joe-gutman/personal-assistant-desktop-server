from quart import websocket, Blueprint

chat_socket_bp = Blueprint("chat_socket", __name__)

@chat_socket_bp.websocket("/ws/chat")
async def chat_ws():
    print("WebSocket connected for chat")
    try:
        await websocket.accept()  # Explicit accept
        while True:
            data = await websocket.receive_json()
            print(f"Received: {data}")
            await websocket.send_json({"echo": data})
    except Exception as e:
        print("WebSocket error:", e)
        await websocket.close()