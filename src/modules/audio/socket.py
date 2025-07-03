from quart import websocket, Blueprint
from .service import handle_audio_stream

audio_socket_bp = Blueprint("audio_socket", __name__)

@audio_socket_bp.websocket("/ws/audio")
async def audio_ws():
    await handle_audio_stream(websocket)