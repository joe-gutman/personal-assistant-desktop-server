from src.extensions.db import db
from openai import OpenAI
from quart import current_app
from src.utils.logger import logging
import datetime


class Chat(db.Model):
    __tablename__ = "chat"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    response = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    @classmethod
    def create_chat(cls, params):
        if not isinstance(params, dict):
            return "Invalid parameters format.", 400

        user_id = params.get("user_id")
        message = params.get("message")
        if not user_id or not message:
            return "User ID and message are required.", 400

        try:
            current_app.logger.info("Initializing OpenAI client...")
            openai_client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
            current_app.logger.info("OpenAI client initialized.")

            current_app.logger.info("Creating chat...")
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )

            if not response.choices or not hasattr(response.choices[0], "message"):
                return "Invalid response from OpenAI.", 500

            chat_response = response.choices[0].message.content 
            chat = cls(user_id=user_id, message=message, response=chat_response)
            db.session.add(chat)
            db.session.commit()
            current_app.logger.info(f"Chat saved to database: {chat}")
            return chat, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create chat: {str(e)}")
            return str(e), 500

        

    @classmethod
    def get_chat_history(cls, user_id, params=None):
        user = cls.query.filter_by(user_id=user_id).all()
        if not user:
            return "User not found.", 404

        max_amount = 100
        amount = max_amount
        date = None

        if params is not None:
            try:
                date_str = params.get("date")
                date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
            except ValueError:
                return "Invalid date format. Use YYYY-MM-DD.", 400
            
            try:
                amount = int(params.get("amount", 0))
                amount = min(amount, max_amount)
            except ValueError:
                amount = max_amount

        query = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).limit(amount)

        if date:
            query = query.filter(db.func.date(cls.created_at) == date)

        try:
            messages = query.all()
        except Exception as e:
            return str(e), 500

        if not messages:
            if date:
                return "No messages found for the given date.", 404
            else:
                return "No messages found.", 404

        return messages, 200
