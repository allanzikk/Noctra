from flask import Blueprint, request, jsonify
from .services import authFunctions
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, set_access_cookies




auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    response = authFunctions.login_service(data)
    return response

@auth_bp.route("/create-account", methods=["POST"])
def create_account():
    data = request.get_json()
    response = authFunctions.create_account_service(data)
    return response

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(user_id)
    response = jsonify({"message": "done."})
    set_access_cookies(response, new_access_token)
    return response