from typing import Any

from fastapi import APIRouter

jack_sketch_router = APIRouter(prefix="/titanic/sketch", tags=["sketch"])


@jack_sketch_router.get("/sketch", response_model=int)
async def get_sketch(request: dict[str, Any]) -> int:
    pass
