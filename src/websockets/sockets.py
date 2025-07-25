import logging
from quart import websocket, Blueprint
from .service import communication_service

logger = logging.getLogger(__name__)

websocket_bp = Blueprint("websocket", __name__)

# Client stream only 

@websocket_bp.websocket("/ws")
async def assistant_ws():
    logger.info("WebSocket connected")
    await websocket.accept()
    communication_service.register_websocket(websocket)
    
    try:
        while True:
            message = await websocket.receive()
            logger.debug(f"Websocket Received: {message[:5]}")
            await communication_service.process_client_message(message)   
    except Exception as e:
        logger.debug("Websocket Error:", e)
    finally:
        logger.info("WebSocket closed")
        await websocket.close(code=1000, reason="[CLIENT STREAM] Stream closed")