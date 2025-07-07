import logging
import os
from quart import Quart
from dotenv import load_dotenv

from .modules import websocket_bp
from .extensions.logging_config import setup_logging

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

assert os.getenv("HUGGINGFACE_TOKEN"), "HUGGINGFACE_TOKEN not loaded from .env!"

def create_app():
    app = Quart(__name__)
    app.register_blueprint(websocket_bp)
    logger.info("Quart app initialized.")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()