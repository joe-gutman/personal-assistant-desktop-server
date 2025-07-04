from quart import Quart
from dotenv import load_dotenv

load_dotenv()

DEBUG = True

# Import websocket blueprints
from .modules import input_socket_bp, output_socket_bp

def create_app():
    app = Quart(__name__)
    app.register_blueprint(input_socket_bp)
    app.register_blueprint(output_socket_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()