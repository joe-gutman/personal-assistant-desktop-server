from quart import current_app, Blueprint, jsonify, request
from src.modules.chats.models import Chat
from src.modules.chats.schemas import ChatSchema

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["POST"])
async def create_chat():
    try: 
        chat_schema = ChatSchema()
        data = await request.get_json()
        params = chat_schema.load(data)  # validates input
        chat, status_code = Chat.create_chat(params)  # chat is the model instance with .response
        current_app.logger.info(f"Chat created: {chat}")
        return jsonify(chat_schema.dump(chat)), status_code  # response field will be included
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return str(e), 500

@chat_bp.route("/<int:user_id>/history", methods=["GET"])
async def get_chat_history(user_id):
    try:
        response, status_code = Chat.get_chat_history(user_id)
        chat_schema = ChatSchema(many=True)
        return jsonify(chat_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500
    

