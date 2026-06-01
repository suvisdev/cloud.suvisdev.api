from typing import Any

from fastapi import APIRouter

ruth_corset_router = APIRouter(prefix="/titanic/corset", tags=["corset"])


@ruth_corset_router.get("/corset", response_model=int)
async def get_corset(request: dict[str, Any]) -> int:
    pass
