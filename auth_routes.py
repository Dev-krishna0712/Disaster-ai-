"""
Authentication Routes
User registration, credential login, JWT distribution, and profile verification.
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.database import db
from app.models.user import User
from app.schemas.validators import UserRegisterSchema, UserLoginSchema
from app.utils.auth_guard import generate_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    try:
        validated = UserRegisterSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    if User.query.filter_by(username=validated.username).first():
        return jsonify({"error": "Username is already taken"}), 409

    if User.query.filter_by(email=validated.email).first():
        return jsonify({"error": "Email is already registered"}), 409

    user = User(
        username=validated.username,
        email=validated.email,
        role=validated.role,
        full_name=validated.full_name,
        phone=validated.phone,
        organization=validated.organization,
    )
    user.set_password(validated.password)

    db.session.add(user)
    db.session.commit()

    token = generate_token(user)
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": user.to_dict(include_sensitive=True)
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    try:
        validated = UserLoginSchema(**data)
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    user = User.query.filter_by(username=validated.username).first()
    if not user or not user.check_password(validated.password):
        return jsonify({"error": "Invalid username or password"}), 401

    token = generate_token(user)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(include_sensitive=True)
    }), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return jsonify({
        "user": current_user.to_dict(include_sensitive=True)
    }), 200
