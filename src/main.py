from quart import Quart
from dotenv import load_dotenv
import os

load_dotenv()

from .modules import websocket_blueprints

def create_app():
    app = Quart(__name__)

    for bp in websocket_blueprints:
        app.register_blueprint(bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()