from extensions import db, bcrypt
from models import User
from utils import error, success
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies
import re
from flask import jsonify

class authFunctions():
    def login_service(data):
        email = data.get("email")
        password = data.get("password")
        if not (email and password):
            return error(code="INVALID_DATA", message="password and email are required.")
        user = User.query.filter_by(email=email).first()
        if user is None:
            response = False
        else:
            response = bcrypt.check_password_hash(user.password_hash, password)
        if not response:
            return error(code="INVALID_DATA", message="invalid credentials.")
        
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        response = jsonify({"message": "done."})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response
    
    def create_account_service(data):
        email = data.get("email")
        password = data.get("password")
        if not (email and password):
            return error(code="INVALID_DATA", message="password and username are required.")
        
        if not 3 <= len(email) <= 254:
            return error("EMAIL_INVALID_DATA", message="email out of limits (3-254).")

        if not 8 <= len(password) <= 72:
            return error("PASSWORD_INVALID_DATA", message="password out of limits (8-72).")
        
        regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        is_valid = re.match(regex, email)
        if not is_valid:
            return error(code="EMAIL_INVALID_DATA", message="invalid email.")

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            return error(code="EMAIL_CONFLICT", message="email is already being used.", status=409)
        
        display_name = data.get("display_name")
        if not display_name:
            display_name = email.split("@")[0][:20]
        else:
            display_name = display_name[:20]

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(display_name=display_name, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return success(message="account created.")
        