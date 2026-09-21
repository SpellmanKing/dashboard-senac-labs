from fastapi import APIRouter
from app.api.v1.endpoints import labs

api_router = APIRouter()
api_router.include_router(labs.router)
