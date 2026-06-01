from typing import Any

from fastapi import APIRouter

isidor_bed_router = APIRouter(prefix="/titanic/bed", tags=["bed"])


@isidor_bed_router.get("/bed", response_model=int)
async def get_bed(request: dict[str, Any]) -> int:
    pass
