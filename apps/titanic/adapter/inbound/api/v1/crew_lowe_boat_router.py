from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.dependencies.crew_lowe_boat import get_crew_lowe_boat_use_case

crew_lowe_boat_router = APIRouter(prefix="/titanic/boat", tags=["boat"])


@crew_lowe_boat_router.get("/boat", response_model=int)
async def get_boat(
    use_case: LoweBoatUseCase = Depends(get_crew_lowe_boat_use_case),
) -> int:
    return await use_case.get_boat({})
