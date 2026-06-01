from typing import Any

from fastapi import APIRouter

hartley_violin_router = APIRouter(prefix="/titanic/violin", tags=["violin"])


@hartley_violin_router.get("/violin", response_model=int)
async def get_violin(request: dict[str, Any]) -> int:
    pass
