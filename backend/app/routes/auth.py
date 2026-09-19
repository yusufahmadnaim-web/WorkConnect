from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from app.extensions import db
from app.models.user import User


class RegisterResource(Resource):
    def post(self):
        data = request.get_json() or {}

        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "customer")

        if not full_name or not email or not password:
            return {
                "message": "full_name, email and password are required"
            }, 400

        email = email.strip().lower()

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return {
                "message": "A user with this email already exists"
            }, 409

        allowed_roles = {"customer", "worker"}

        if role not in allowed_roles:
            return {
                "message": "Invalid role"
            }, 400

        user = User(
            full_name=full_name.strip(),
            email=email,
            role=role,
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            },
        }, 201


class LoginResource(Resource):
    def post(self):
        data = request.get_json() or {}

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {
                "message": "email and password are required"
            }, 400

        email = email.strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {
                "message": "Invalid email or password"
            }, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role,
            },
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            },
        }, 200

 
class MeResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        user = db.session.get(User, int(user_id))

        if not user:
            return {
                "message": "User not found"
            }, 404

        return {
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
            }
        }, 200