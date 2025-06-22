from quart import Quart, websocket
from quart_sqlalchemy import SQLAlchemyConfig
from quart_sqlalchemy.framework import QuartSQLAlchemy
from quart.cli import with_appcontext
from config import Config
from dotenv import load_dotenv
from src.modules import register_blueprints
from src.modules import register_websockets
from src.extensions import register_extensions
from src.extensions.db import db

import click
import os
import asyncio

load_dotenv()

def create_app():
    app = Quart(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Now pass db to your modules
    register_extensions(app)
    register_blueprints(app)
    register_websockets(app)


    register_extensions(app)
    register_blueprints(app)
    register_websockets(app)

    @click.command("create-db")
    @with_appcontext
    def create_db():
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        print(f"DB_URI: {db_uri}")

        try:
            if not database_exists(db_uri):
                create_database(db_uri)
                print(f"Database {Config.DB_NAME} created!")
            else:
                print("Database already exists.")
        except Exception as e:
            print(f"Failed to check or create database: {e}")
            return

        try:
            db.create_all()
            print("Tables created!")
        except Exception as e:
            print(f"Failed to create tables: {e}")

    app.cli.add_command(create_db)  # Register the command with Quart's CLI

    return app

if __name__ == "__main__":
    app = create_app()
    print("DB_HOST:", os.getenv('DB_HOST'))
    app.run(debug=False)