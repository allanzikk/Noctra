from flask import Flask
from extensions import jwt, bcrypt, db, migrate, cors
from dotenv import load_dotenv
import os
from auth.routes import auth_bp
from sessions.routes import sessions_bp
from datetime import timedelta



def create_app():
    load_dotenv()

    app = Flask(__name__)

    
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_COOKIE_SAMESITE"] = "None"
    app.config["JWT_COOKIE_SECURE"] = True
    app.json.sort_keys = False

    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True, origins=[os.getenv("CLIENT_URL")])



    app.register_blueprint(auth_bp)
    app.register_blueprint(sessions_bp)

    return app