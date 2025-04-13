from flask import Blueprint, request, jsonify
from .models import User
from .schemas import UserSchema
from src.main import db

user_bp = Blueprint('user', __name__)

@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    user_data = UserSchema().load(data)  
    user = User(**user_data)             
    db.session.add(user)
    db.session.commit()
    return UserSchema().dump(user), 201

@user_bp.route("/", methods=["GET"])
def get_users():
    try:
        response, status_code = User.get_all_users()
        user_schema = UserSchema(many=True)
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500
    
@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        response, status_code = User.get_user_by_id(user_id)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500
    
@user_bp.route("/<string:username>", methods=["GET"])
def get_user_by_name(username):
    try:
        response, status_code = User.get_user_by_name(username)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500

def get_chat_history(user_id):
    params = request.args
    try:
        response, status_code = User.get_chat_history(user_id, params)
        chat_schema = ChatSchema(many=True)
        return jsonify(chat_schema.dump(response)), status_code
    except Exception as e:
        return str(e), 500