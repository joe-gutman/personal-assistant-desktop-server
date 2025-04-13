from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
import click
from sqlalchemy_utils import database_exists, create_database
from config import Config
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from src.blueprints import user_bp, chat_bp
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

    # Initialize extensions
    db.init_app(app)

    # Register CLI commands
    @click.command("create-db")
    @with_appcontext
    def create_db():
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        print(f"DB_URI: {db_uri}")

        try:
            if not database_exists(db_uri):
                create_database(db_uri)
                print(f"✅ Database {Config.DB_NAME} created!")
            else:
                print("Database already exists.")
        except Exception as e:
            print(f"❌ Failed to check or create database: {e}")
            return

        try:
            db.create_all()
            print("✅ Tables created!")
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")

    app.cli.add_command(create_db)  # Register the command with Flask's CLI

    return app

# Create the Flask app instance
app = create_app()

# Run the app if executed directly
if __name__ == "__main__":
    print("DB_HOST:", os.getenv('DB_HOST'))
    app.run(debug=True)
