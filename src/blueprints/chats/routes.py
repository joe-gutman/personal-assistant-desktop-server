from flask import Blueprint, jsonify, request
from src.blueprints.chats.models import Chat
from src.blueprints.chats.schema import ChatSchema
from src.main import db

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["POST"])
def create_chat():
    data = request.get_json()
    chat = Chat(**data)
    db.session.add(chat)
    db.session.commit()
    return jsonify({"message": "Chat created successfully"}), 201

@chat_bp.route("/<int:user_id>/history", methods=["GET"])
def get_chat_history(user_id):
    # sort by create_at in descending order
    params = request.args
    chats = Chat.get_chat_history(user_id, params)
    chat_schema = ChatSchema(many=True)
    return jsonify(chat_schema.dump(chats))

