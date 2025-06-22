from quart import current_app, Blueprint, jsonify, request
from .models import User
from .schemas import UserSchema

user_bp = Blueprint('user', __name__)

@user_bp.route("/", methods=["POST"])
async def create_user():
    try:
        data = await request.get_json()
        response, status_code = User.create_user(data)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500

@user_bp.route("/", methods=["GET"])
async def get_users():
    try:
        response, status_code = User.get_all_users()
        user_schema = UserSchema(many=True)
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500
    
@user_bp.route("/<int:user_id>", methods=["GET"])
async def get_user_by_id(user_id):
    try:
        response, status_code = User.get_user_by_id(user_id)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500
    
@user_bp.route("/<string:username>", methods=["GET"])
async def get_user_by_name(username):
    try:
        response, status_code = User.get_user_by_name(username)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500

async def get_chat_history(user_id):
    params = request.args
    try:
        response, status_code = User.get_chat_history(user_id, params)
        chat_schema = ChatSchema(many=True)
        return jsonify(chat_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500