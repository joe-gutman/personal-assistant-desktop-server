from .chat import chat_socket_bp
from .audio import audio_socket_bp

websocket_blueprints = [chat_socket_bp, audio_socket_bp]