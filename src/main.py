from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from sqlalchemy_utils import database_exists, create_database
from config import Config
from dotenv import load_dotenv
from src.blueprints import user_bp, chat_bp
from src.extensions import db, migrate
import click
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)

    register_blueprints(app)

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

    app.cli.add_command(create_db)  # Register the command with Flask's CLI

    return app

def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

if __name__ == "__main__":
    app = create_app()
    print("DB_HOST:", os.getenv('DB_HOST'))
    app.run(debug=True)