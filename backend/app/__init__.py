from flask import Flask
from sqlalchemy import text


from app.config import Config
from app.extensions import db, migrate, jwt, cors
from app.models.user import User
from flask_restful import Api
from app.routes.workers import WorkerProfileResource
from app.routes.auth import (
    RegisterResource,
    LoginResource,
    MeResource,
)


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)


    api = Api(app)

    api.add_resource(RegisterResource, "/api/auth/register")
    api.add_resource(LoginResource, "/api/auth/login")
    api.add_resource(MeResource, "/api/auth/me")
    api.add_resource(
    WorkerProfileResource,
    "/api/workers/profile",
)



    @app.route("/")
    def home():
        return {"message": "WorkConnect API is running"}

    @app.route("/health/db")
    def database_health():
        db.session.execute(text("SELECT 1"))
        return {"message": "Database connection successful"}

    return app