import jwt
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import sessionFunctions
from utils import success


sessions_bp = Blueprint('sessions', __name__)


@sessions_bp.route('/sessions/start', methods=['POST'])
@jwt_required()
def start_session():
    user_id = get_jwt_identity()
    token = sessionFunctions.create_session_token(user_id)
    return success(data={"session_token": token})

@sessions_bp.route('/sessions/complete', methods=['POST'])
@jwt_required()
def complete_session():
    user_id = get_jwt_identity()
    data = request.get_json()
    response = sessionFunctions.complete_session(self=sessionFunctions, data=data, user_id=user_id)
    return response

@sessions_bp.route('/sessions/history')
@jwt_required()
def get_sessions():
    user_id = get_jwt_identity()
    before_cursor = request.args.get("before")
    limit = request.args.get("limit")
    response = sessionFunctions.get_sessions(before_cursor, limit, user_id)
    return response

@sessions_bp.route('/sessions/stats')
@jwt_required()
def total_sessions():
    user_id = get_jwt_identity()
    response = sessionFunctions.total_sessions(user_id)
    return response