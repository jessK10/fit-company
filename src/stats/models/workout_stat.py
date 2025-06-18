from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base
from datetime import datetime

class WorkoutStat(Base):
    __tablename__ = "workout_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    workout_type = Column(String, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Integer, nullable=False)
    performed_at = Column(DateTime, default=datetime.utcnow)
