from src.main import db
from sqlalchemy.exc import IntegrityError
from config import Config
from openai import OpenAI
import datetime


class Chat(db.Model):
    __tablename__ = "chat"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(1000), nullable=False)
    response = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    @classmethod
    def create_chat(cls, user_id, message, response=None):
        try:
            chat = cls(user_id=user_id, message=message, response=response)
            db.session.add(chat)
            db.session.commit()
            return chat, 201
        except IntegrityError:
            db.session.rollback()
            return "User ID does not exist.", 400
        except Exception as e:
            db.session.rollback()
            return str(e), 500

    @classmethod
    def get_chat_history(cls, user_id, params):
        user = cls.query.filter_by(user_id=user_id).all()
        if not user:
            return "User not found.", 404

        max_amount = 100
        messages = None

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