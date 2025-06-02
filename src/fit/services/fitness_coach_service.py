import requests
from src.fit.models_dto import WodResponseSchema

COACH_SERVICE_URL = "http://coach:8001/wod"

def request_wod_from_microservice(user_email: str, exclude_ids: list[int]) -> WodResponseSchema:
    response = requests.post(
        COACH_SERVICE_URL,
        json={"email": user_email, "exclude_ids": exclude_ids},
        timeout=10
    )
    response.raise_for_status()
    return WodResponseSchema.model_validate(response.json())
