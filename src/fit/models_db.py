from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Table, Text, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class UserModel(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Profile information (nullable as they'll be filled during onboarding)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    fitness_goal = Column(String, nullable=True)
    onboarded = Column(String, default="false", nullable=False)

    # Relationships
    workouts = relationship("WorkoutModel", back_populates="user")

    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}', role='{self.role}')>"

class WorkoutModel(Base):
    __tablename__ = 'workouts'
    
    id = Column(Integer, primary_key=True)
    user_email = Column(String, ForeignKey('users.email'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    performed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="workouts")
    exercises = relationship("UserExerciseHistory", back_populates="workout")

    def __repr__(self):
        return f"<Workout(id={self.id}, user_email='{self.user_email}', created_at='{self.created_at}', performed_at='{self.performed_at}')>"

class UserExerciseHistory(Base):
    __tablename__ = 'user_exercise_history'
    
    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'), nullable=False)
    exercise_id = Column(Integer, nullable=False)
    
    # Relationships
    workout = relationship("WorkoutModel", back_populates="exercises")

    def __repr__(self):
        return f"<UserExerciseHistory(id={self.id}, workout_id='{self.workout_id}', exercise_id='{self.exercise_id}')>"