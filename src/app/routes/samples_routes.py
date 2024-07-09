from app.utils.auth import auth
from fastapi import APIRouter, Security

router = APIRouter()


@router.get("/")
def get_samples(auth_result: str = Security(auth.verify)):
    return {"msg": "Hello, World!"}
