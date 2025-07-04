from quart import websocket, Blueprint
from .service import communication_service

client_stream_bp = Blueprint("client_stream", __name__)
server_stream_bp = Blueprint("server_stream", __name__)

# Client stream only 

@client_stream_bp.websocket("/ws/client")
async def audio_ws():
    print("WebSocket connected: CLIENT STREAM")
    await websocket.accept()
    communication_service.register_client_stream(websocket)
    
    try:
        while True:
            message = await websocket.receive()
            print(f"[CLIENT STREAM] Received: {message}")
            await communication_service.process_audio_message(message)
    except Exception as e:
        print("[CLIENT STREAM] Error:", e)
    finally:
        await websocket.close(code=1000, reason="[CLIENT STREAM] Stream closed")
    

@server_stream_bp.websocket("/ws/server")
async def output_ws():
    print("WebSocket connected: SERVER STREAM")
    await websocket.accept()
    communication_service.register_server_stream(websocket)
    
    try:
        while True:
            await websocket.receive()
    except Exception as e:
        print("[SERVER STREAM] Error:", e)
    finally:
        await websocket.close(code=1000, reason="[SERVER STREAM] Stream closed")
        
        
