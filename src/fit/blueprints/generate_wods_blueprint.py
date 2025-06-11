from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from src.fit.database import engine
from src.fit.models_db import UserModel

from src.fit.services.rabbitmq_service import rabbitmq_service
import json, datetime

generate_wods_bp = Blueprint("generate_wods", __name__)

@generate_wods_bp.route("/generateWods", methods=["POST"])
def generate_wods():
    session = Session(bind=engine)
    users = session.query(UserModel).all()
    channel = channel = rabbitmq_service.channel


    for user in users:
        message = {
            "user_id": user.id,
            "username": user.username,
            "date": str(datetime.date.today()),
            "retry_count": 0
        }
        channel.basic_publish(
            exchange="",
            routing_key="createWodQueue",
            body=json.dumps(message)
        )

    return jsonify({"status": "WOD jobs sent"}), 202
