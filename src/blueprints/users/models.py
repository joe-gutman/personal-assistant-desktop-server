from src.extensions import db
from src.blueprints.chats.models import Chat
from datetime import datetime
from sqlalchemy.exc import IntegrityError
# import logging

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    chat_history = db.relationship(Chat, backref="user", lazy="dynamic")

    @classmethod
    def create_user(cls, data):
        new_user = User(
            username=data['username'], 
            password=data['password'], 
            email=data['email'])
        db.session.add(new_user)
        try:
            db.session.commit()
            return new_user, 201
        except IntegrityError:
            db.session.rollback()
            return "Username or email already exists.", 400

    @staticmethod
    def get_all_users():
        users = User.query.all()
        if not users:
            return "No users found.", 404
        return users, 200
        
    @staticmethod
    def get_user_by_name(username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return "User not found.", 404
        return user, 200

    @staticmethod
    def get_user_by_id(user_id):
        user = User.query.get(user_id)
        if not user:
            return "User not found.", 404
        return user, 200

    @classmethod
    def get_chat_history(cls, user_id, params):
        user = cls.query.get(user_id)
        if not user:
            return "User not found.", 404

        try:
            date_str = params.get("date")
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
        except ValueError:
            return "Error with date. Make sure the date is in the format: YYYY-MM-DD.", 400

        try:
            amount = int(params.get("amount", 0))
            amount = min(amount, 100)  # Limit to 100 messages
        except ValueError:
            amount = 100

        query = Chat.query.filter_by(user_id=user_id).order_by(Chat.created_at.desc()).limit(amount)

        if date:
            query = query.filter(db.func.date(Chat.created_at) == date)

        try:
            messages = query.all()
        except IntegrityError as e:
            # logging.error(f"Database integrity error: {e}")
            return "Database integrity error.", 500
        except Exception as e:
            # logging.error(f"Unexpected error: {e}")
            return "An unexpected error occurred.", 500

        if not messages:
            if date:
                return "No messages found for the given date.", 404
            else:
                return "No messages found.", 404

        return messages, 200
            