from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import random

app = FastAPI()

class MuscleGroupImpact(BaseModel):
    id: int
    name: str
    body_part: str
    is_primary: bool
    intensity: float

class WodExerciseSchema(BaseModel):
    id: int
    name: str
    description: str
    difficulty: float
    muscle_groups: List[MuscleGroupImpact]
    suggested_weight: float
    suggested_reps: int

class WodResponseSchema(BaseModel):
    exercises: List[WodExerciseSchema]
    generated_at: str

class ExerciseRequest(BaseModel):
    email: str
    exclude_ids: List[int]

exercise_pool = [{
    "id": i,
    "name": f"Exercise {i}",
    "description": f"Description for exercise {i}",
    "difficulty": random.uniform(1, 5)
} for i in range(1, 21)]

@app.post("/wod", response_model=WodResponseSchema)
def generate_wod(request: ExerciseRequest):
    filtered = [ex for ex in exercise_pool if ex["id"] not in request.exclude_ids]
    if len(filtered) < 5:
        raise HTTPException(status_code=400, detail="Not enough exercises.")

    selected = random.sample(filtered, 5)
    wod_exercises = []

    for ex in selected:
       wod_exercises.append(WodExerciseSchema(
    id=ex["id"],
    name=ex["name"],
    description=ex["description"],
    difficulty=int(ex["difficulty"]),  
    muscle_groups=[
        MuscleGroupImpact(
            id=1,
            name="Chest",
            body_part="Upper",
            is_primary=True,
            intensity=float(ex["difficulty"] * 1.2)
        )
    ],
    suggested_weight=random.uniform(5, 50),
    suggested_reps=random.randint(8, 15)
))


    return WodResponseSchema(
        exercises=wod_exercises,
        generated_at=datetime.utcnow().isoformat()
    )
