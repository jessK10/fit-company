import logging
from flask import Flask, request, jsonify
from pydantic import ValidationError

from .models_dto import UserSchema

from .database import init_db, db_session
from .models_db import UserModel
from .services.user_service import create_user as create_user_service
from .blueprints import user_bp, auth_bp, workout_bp
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create Flask app
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

# Force stdout to be unbuffered
import sys
sys.stdout.reconfigure(line_buffering=True)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/')
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(workout_bp, url_prefix='/workouts')

BOOTSTRAP_KEY = os.environ.get("BOOTSTRAP_KEY", "bootstrap-secret-key")

@app.route("/health")
def health():
    return {"status": "UP"}

@app.route("/bootstrap/admin", methods=["POST"])
def create_bootstrap_admin():
    try:
        # This endpoint should be secured with a special bootstrap key
        bootstrap_key = request.headers.get('X-Bootstrap-Key')
        if not bootstrap_key or bootstrap_key != BOOTSTRAP_KEY:
            return jsonify({"error": "Invalid bootstrap key"}), 401
            
        # Check if admin already exists to prevent multiple bootstraps
        db = db_session()
        admin_exists = db.query(UserModel).filter(UserModel.role == "admin").first() is not None
        db.close()
        
        if admin_exists:
            return jsonify({"error": "Admin user already exists"}), 409
            
        # Create admin user
        admin_data = request.get_json()
        admin_data["role"] = "admin"  # Ensure role is admin
        
        admin_user = UserSchema.model_validate(admin_data)
        created_admin = create_user_service(admin_user)
        
        return jsonify(created_admin.model_dump()), 201
        
    except ValidationError as e:
        return jsonify({"error": "Invalid admin data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error creating admin", "details": str(e)}), 500

def run_app():
    """Entry point for the application script"""
    # Initialize the database before starting the app
    init_db()

    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_app()

