from app.utils.auth import auth
from fastapi import APIRouter, Security
from typing import Dict, Any

router = APIRouter()


@router.get("/")
def get_samples(auth_result: Dict[str, Any] = Security(auth.verify)):
    return {"msg": "Hello, World!"}
