from flask import Blueprint
from .users.routes import user_bp
from .chats.routes import chat_bp

def init_app(app):
    # Register each blueprint with the app
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
