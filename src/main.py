from quart import Quart
from dotenv import load_dotenv

load_dotenv()

DEBUG = True

# Import websocket blueprints
from .modules import client_stream_bp, server_stream_bp

def create_app():
    app = Quart(__name__)
    app.register_blueprint(client_stream_bp)
    app.register_blueprint(server_stream_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()