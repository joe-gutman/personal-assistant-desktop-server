from quart import Blueprint
from .users.routes import user_bp
from .chats.routes import chat_bp
from .chats.sockets import chat_ws
from .audio.sockets import audio_ws

def register_blueprints(app):
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

def register_websockets(app):
    app.add_websocket('/ws/chat', chat_ws)
    app.add_websocket('/ws/audio', audio_ws)