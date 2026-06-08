from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.dependencies.crew_smith_captain import get_crew_smith_captain_use_case

crew_smith_captain_router = APIRouter(prefix="/titanic/captain", tags=["captain"])


@crew_smith_captain_router.get("/captain", response_model=int)
async def get_captain(
    use_case: SmithCaptainUseCase = Depends(get_crew_smith_captain_use_case),
) -> int:
    return await use_case.get_captain({})
