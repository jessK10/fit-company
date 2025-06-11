from flask import Blueprint, request, jsonify, g
from pydantic import ValidationError
from ..models_dto import UserSchema, UserProfileSchema
from fit.services.user_service import (
    create_user as create_user_service,
    get_all_users as get_all_users_service,
    update_user_profile,
    get_user_profile
)
from ..services.auth_service import admin_required, jwt_required
from ..services.rabbitmq_service import rabbitmq_service
import os

user_bp = Blueprint('user', __name__)

BOOTSTRAP_KEY = os.environ.get("BOOTSTRAP_KEY", "bootstrap-secret-key")

@user_bp.route("/users", methods=["POST"])
@admin_required
def create_user():
    try:
        user_data = request.get_json()
        user = UserSchema.model_validate(user_data)
        created_user = create_user_service(user)
        return jsonify(created_user.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": "Invalid user data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating user", "details": str(e)}), 500

@user_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = get_all_users_service()
        return jsonify([user.model_dump() for user in users]), 200
    except Exception as e:
        return jsonify({"error": "Error retrieving users", "details": str(e)}), 500

@user_bp.route("/users/generateWods", methods=["POST"])
@admin_required
def generate_wods():
    try:
        # Get all users
        users = get_all_users_service()
        
        # Queue a WOD generation job for each user
        for user in users:
            message = {"email": user.email}
            rabbitmq_service.publish_message(message)
        
        return jsonify({
            "message": f"Queued WOD generation for {len(users)} users",
            "queue": "createWodQueue"
        }), 202
        
    except Exception as e:
        return jsonify({
            "error": "Error queueing WOD generation",
            "details": str(e)
        }), 500

@user_bp.route("/profile/onboarding", methods=["POST"])
@jwt_required
def onboard_user():
    try:
        # Get user email from the JWT token (set by the jwt_required decorator)
        user_email = g.user_email
        
        # Parse and validate the profile data
        profile_data = request.get_json()
        profile = UserProfileSchema.model_validate(profile_data)
        
        # Update the user's profile
        updated_profile = update_user_profile(user_email, profile)
        if not updated_profile:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(updated_profile.model_dump()), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid profile data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error updating profile", "details": str(e)}), 500

@user_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    try:
        # Get user email from the JWT token
        user_email = g.user_email
        
        # Get the user's profile
        profile = get_user_profile(user_email)
        if not profile:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(profile.model_dump()), 200
        
    except Exception as e:
        return jsonify({"error": "Error retrieving profile", "details": str(e)}), 500
