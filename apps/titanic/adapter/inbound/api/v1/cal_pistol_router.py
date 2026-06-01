from typing import Any

from fastapi import APIRouter

cal_pistol_router = APIRouter(prefix="/titanic/pistol", tags=["pistol"])


@cal_pistol_router.get("/pistol")
async def get_pistol(request: dict[str, Any]) -> None:
    pass
