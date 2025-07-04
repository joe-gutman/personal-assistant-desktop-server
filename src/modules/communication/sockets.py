from quart import websocket, Blueprint
from .service import communication_service

input_socket_bp = Blueprint("input_socket", __name__)
output_socket_bp = Blueprint("output_socket", __name__)

@input_socket_bp.websocket("/ws/input")
async def audio_ws():
    print("WebSocket connected: INPUT WS")
    await websocket.accept()
    communication_service.register_input_socket(websocket)
    
    try:
        while True:
            message = await websocket.receive()
            print(f"[Audio] Received: {message}")
            await communication_service.process_audio_message(message)
    except Exception as e:
        print("[INPUT WS] Error:", e)
    finally:
        await websocket.close(code=1000, reason="[INPUT WS] Stream closed")
    

@output_socket_bp.websocket("/ws/output")
async def output_ws():
    print("WebSocket connected: OUTPUT WS")
    await websocket.accept()
    
    try:
        while True:
            await websocket.receive()
    except Exception as e:
        print("[OUTPUT WS] Error:", e)
    finally:
        await websocket.close(code=1000, reason="[OUTPUT WS] Stream closed")
        
        
