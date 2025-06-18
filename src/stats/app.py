from flask import Flask, jsonify, request
from models.workout_stat import WorkoutStat, Base  
from db.database import SessionLocal, engine        
from queue_consumer import start_consumer
import threading
from datetime import datetime


app = Flask(__name__)

Base.metadata.create_all(bind=engine)

# Start the queue consumer in a background thread
threading.Thread(target=start_consumer, daemon=True).start()

@app.route("/stats/", methods=["GET"])
def get_stats():
    db = SessionLocal()
    try:
        stats = db.query(WorkoutStat).all()
        return jsonify([
    {
        "user_id": s.user_id,
        "workout_type": s.workout_type,
        "duration_minutes": s.duration_minutes,
        "calories_burned": s.calories_burned,
        "performed_at": s.performed_at.isoformat()
    } for s in stats
])

    finally:
        db.close()

@app.route("/stats/", methods=["POST"])
def create_stat():
    db = SessionLocal()
    data = request.json

    new_stat = WorkoutStat(
        user_id=data["user_id"],
        workout_type=data["workout_type"],
        duration_minutes=data["duration_minutes"],
        calories_burned=data["calories_burned"],
        performed_at=datetime.utcnow()
    )
    db.add(new_stat)
    db.commit()
    db.refresh(new_stat)
    
    return jsonify({
        "user_id": new_stat.user_id,
        "workout_type": new_stat.workout_type,
        "duration_minutes": new_stat.duration_minutes,
        "calories_burned": new_stat.calories_burned,
        "performed_at": new_stat.performed_at.isoformat()
    }), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
