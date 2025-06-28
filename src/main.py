from quart import Quart
from dotenv import load_dotenv

load_dotenv()

from .modules import chat_socket_bp
from .modules import audio_socket_bp

def create_app():
    app = Quart(__name__)
    app.register_blueprint(audio_socket_bp)
    app.register_blueprint(chat_socket_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()