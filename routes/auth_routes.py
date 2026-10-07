from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from extensions import db
from models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =========================================================
# REGISTER
# =========================================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "doctor")

    if not name:
        return jsonify({
            "message": "Name is required"
        }), 400

    if not email:
        return jsonify({
            "message": "Email is required"
        }), 400

    if not password:
        return jsonify({
            "message": "Password is required"
        }), 400

    # Only these roles are allowed
    if role not in ["doctor", "patient"]:
        return jsonify({
            "message": "Role must be doctor or patient"
        }), 400

    # Check duplicate email
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    user = User(
        name=name,
        email=email,
        role=role
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 201


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "JSON body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email:
        return jsonify({
            "message": "Email is required"
        }), 400

    if not password:
        return jsonify({
            "message": "Password is required"
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not user.check_password(password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    # JWT claims
    claims = {
        "role": user.role,
        "name": user.name
    }

    # Add doctor ID for doctor accounts
    if user.role == "doctor":
        claims["doctor_id"] = user.doctor_id

    # Add patient ID for patient accounts
    if user.role == "patient":
        claims["patient_id"] = user.patient_id

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=claims
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "doctor_id": user.doctor_id,
            "patient_id": user.patient_id
        }
    }), 200


# =========================================================
# PROFILE
# =========================================================

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "message": "User not found"
        }), 404

    claims = get_jwt()

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": claims.get("role"),
        "doctor_id": user.doctor_id,
        "patient_id": user.patient_id
    }), 200