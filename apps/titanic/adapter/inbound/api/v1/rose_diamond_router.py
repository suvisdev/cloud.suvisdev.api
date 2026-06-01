from typing import Any

from fastapi import APIRouter
rose_diamond_router = APIRouter(prefix="/titanic/diamond", tags=["diamond"])


@rose_diamond_router.get("/diamond", response_model=int)
async def get_diamond(request: dict[str, Any]) -> int:
    pass
