from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from ..models_dto import LoginSchema, TokenSchema
from fit.services.auth_service import authenticate_user, create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/oauth/token", methods=["POST"])
def login():
    try:
        # Check if content type is application/x-www-form-urlencoded (OAuth standard)
        content_type = request.headers.get('Content-Type', '')
        if 'application/x-www-form-urlencoded' in content_type:
            login_data = {
                "email": request.form.get("username"),  # OAuth uses 'username' 
                "password": request.form.get("password")
            }
        else:  # Fallback to JSON
            login_data = request.get_json()
            
        login_schema = LoginSchema.model_validate(login_data)
        
        user = authenticate_user(login_schema.email, login_schema.password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Create access token with standard OAuth claims
        access_token_expires = datetime.timedelta(minutes=30)
        token_data = {
            "sub": user.email,
            "name": user.name,
            "role": user.role,
            "iss": "fit-api", 
            "iat": datetime.datetime.now(datetime.UTC), 
        }
        
        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )
        
        token = TokenSchema(
            access_token=access_token,
            token_type="bearer"
        )
        
        # Include onboarding status in response
        response_data = token.model_dump()
        response_data["onboarded"] = user.onboarded
        
        return jsonify(response_data), 200
        
    except ValidationError as e:
        return jsonify({"error": "Invalid login data", "details": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": "Error logging in", "details": str(e)}), 500
