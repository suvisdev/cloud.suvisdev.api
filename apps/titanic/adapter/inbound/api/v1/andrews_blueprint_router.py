from typing import Any

from fastapi import APIRouter
andrews_blueprint_router = APIRouter(prefix="/titanic/andrews", tags=["blueprint"])

@andrews_blueprint_router.get("/blueprint", response_model=int)
async def get_blueprint(request: dict[str, Any]) -> int:
    return 0
