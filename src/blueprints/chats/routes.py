from src.extensions import db
from flask import current_app
from flask import Blueprint, jsonify, request
from src.blueprints.chats.models import Chat
from src.blueprints.chats.schema import ChatSchema

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["POST"])
def create_chat():
    try: 
        chat_schema = ChatSchema()
        params = chat_schema.load(request.json)  # validates input
        chat, status_code = Chat.create_chat(params)  # chat is the model instance with .response
        current_app.logger.info(f"Chat created: {chat}")
        return jsonify(chat_schema.dump(chat)), status_code  # response field will be included
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return str(e), 500

@chat_bp.route("/<int:user_id>/history", methods=["GET"])
def get_chat_history(user_id):
    try:
        response, status_code = Chat.get_chat_history(user_id)
        chat_schema = ChatSchema(many=True)
        return jsonify(chat_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500
    

