from typing import Any

from fastapi import APIRouter

smith_captain_router = APIRouter(prefix="/titanic/captain", tags=["captain"])


@smith_captain_router.get("/captain", response_model=int)
async def get_captain(request: dict[str, Any]) -> int:
    pass
