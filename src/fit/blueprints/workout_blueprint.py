from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..models_dto import  RegisterWorkoutSchema
from ..services.workout_service import get_last_workout_exercises, register_workout
from ..services.auth_service import  api_key_required
from fit.services.rabbitmq_service import rabbitmq_service
from ..models_db import UserModel
from ..database import db_session
from datetime import datetime

workout_bp = Blueprint('workout', __name__)
   

@workout_bp.route("/last", methods=["POST"])
@api_key_required
def get_user_last_workout():
    try:
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "email is required"}), 400
        
        exercises = get_last_workout_exercises(email)
        if exercises is None:
            return jsonify([]), 200
            
        return jsonify([exercise.model_dump() for exercise in exercises]), 200
        
    except Exception as e:
        return jsonify({"error": "Error retrieving last workout", "details": str(e)}), 500 
    
@workout_bp.route("/register", methods=["POST"])
@api_key_required
def perform_workout():
    try:
        workout_data = request.get_json()
        workout = RegisterWorkoutSchema.model_validate(workout_data)
        register_workout(workout.email, workout.exercises)
        return jsonify({"message": "Workout registered successfully"}), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid workout data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error registering workout", "details": str(e)}), 500 
    
@workout_bp.route("/generateWods", methods=["POST"])
@api_key_required
def generate_wods_for_all_users():
    try:
        db = db_session()
        users = db.query(UserModel).all()
        today = datetime.utcnow().date().isoformat()

        for user in users:
            message = {
                "user_id": str(user.id),
                "date": today,
                "retry": 0
            }
            rabbitmq_service.publish_message(message)

        db.close()
        return jsonify({"message": "WOD jobs queued", "user_count": len(users)}), 202

    except Exception as e:
        return jsonify({"error": "WOD generation failed", "details": str(e)}), 500