from flask import Blueprint, request, jsonify, g, current_app
from pydantic import ValidationError

from ..queue_messages import CreateWodMessage
from ..models_dto import UserSchema, UserProfileSchema
from fit.services.user_service import (
    create_user as create_user_service,
    get_all_users as get_all_users_service,
    update_user_profile,
    get_user_profile
)
from ..services.auth_service import admin_required, jwt_required
from ..services.rabbitmq_service import rabbitmq_service
from ..services.workout_service import get_most_recent_workout_exercises
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
        current_app.logger.info(f"Created new user: {user.email}")
        return jsonify(created_user.model_dump()), 201
    except ValidationError as e:
        current_app.logger.warning(f"Invalid user data received: {e.errors()}")
        return jsonify({"error": "Invalid user data", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Error creating user", "details": str(e)}), 500

@user_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    try:
        users = get_all_users_service()
        current_app.logger.debug(f"Retrieved {len(users)} users")
        return jsonify([user.model_dump() for user in users]), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({"error": "Error retrieving users", "details": str(e)}), 500

@user_bp.route("/users/generateWods", methods=["POST"])
@admin_required
def generate_wods():
    try:
        # Get all users
        users = get_all_users_service()
        current_app.logger.info(f"Found {len(users)} total users")
        
        # Filter users who need a new workout
        users_needing_workout = []
        for user in users:
            # Check if user has any unperformed workout
            unperformed_workout = get_most_recent_workout_exercises(user.email, performed=False)
            if unperformed_workout is not None:
                current_app.logger.debug(f"Skipping user {user.email} - has unperformed workout")
                continue
                
            users_needing_workout.append(user)
            current_app.logger.debug(f"User {user.email} has no unperformed workouts - will generate one")
        
        current_app.logger.info(f"Generating WODs for {len(users_needing_workout)} users who need new workouts")
        
        # Queue a WOD generation job for filtered users
        for user in users_needing_workout:
            message = CreateWodMessage(email=user.email)
            rabbitmq_service.publish_message(message)
        
        current_app.logger.info(f"Successfully queued WOD generation for {len(users_needing_workout)} users")
        return jsonify({
            "message": f"Queued WOD generation for {len(users_needing_workout)} users",
            "total_users": len(users),
            "users_needing_workout": len(users_needing_workout),
            "queue": "createWodQueue"
        }), 202
        
    except Exception as e:
        current_app.logger.error(f"Error queueing WOD generation: {str(e)}")
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
        current_app.logger.debug(f"Processing onboarding for user: {user_email}")
        
        # Parse and validate the profile data
        profile_data = request.get_json()
        profile = UserProfileSchema.model_validate(profile_data)
        
        # Update the user's profile
        updated_profile = update_user_profile(user_email, profile)
        if not updated_profile:
            current_app.logger.warning(f"User not found during onboarding: {user_email}")
            return jsonify({"error": "User not found"}), 404
            
        current_app.logger.info(f"Successfully completed onboarding for user: {user_email}")
        return jsonify(updated_profile.model_dump()), 200
        
    except ValidationError as e:
        current_app.logger.warning(f"Invalid profile data for user {g.user_email}: {e.errors()}")
        return jsonify({"error": "Invalid profile data", "details": e.errors()}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating profile for user {g.user_email}: {str(e)}")
        return jsonify({"error": "Error updating profile", "details": str(e)}), 500

@user_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    try:
        # Get user email from the JWT token
        user_email = g.user_email
        current_app.logger.debug(f"Retrieving profile for user: {user_email}")
        
        # Get the user's profile
        profile = get_user_profile(user_email)
        if not profile:
            current_app.logger.warning(f"Profile not found for user: {user_email}")
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(profile.model_dump()), 200
        
    except Exception as e:
        current_app.logger.error(f"Error retrieving profile for user {g.user_email}: {str(e)}")
        return jsonify({"error": "Error retrieving profile", "details": str(e)}), 500
