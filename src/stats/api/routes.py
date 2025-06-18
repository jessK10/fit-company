from flask import Blueprint, jsonify

stats_bp = Blueprint("stats", __name__)

@stats_bp.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Stats service is running!"})
