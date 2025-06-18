from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

Base = declarative_base()

class WorkoutStat(Base):
    __tablename__ = "workout_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    workout_type = Column(String, nullable=False)
    duration_minutes = Column(Float)
    performed_at = Column(DateTime, default=datetime.utcnow)
