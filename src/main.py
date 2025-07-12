import os
from dotenv import load_dotenv

from .extensions.logging_config import setup_logging
setup_logging()

import logging
from quart import Quart
from .modules import websocket_bp

load_dotenv()

logger = logging.getLogger(__name__)

def create_app():
    app = Quart(__name__)
    app.register_blueprint(websocket_bp)
    logger.info("Quart app initialized.")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()