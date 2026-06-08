from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorBedUseCase
from titanic.dependencies.passenger_isidor_couple import get_passenger_isidor_couple_use_case

passenger_isidor_couple_router = APIRouter(prefix="/titanic/bed", tags=["bed"])


@passenger_isidor_couple_router.get("/bed", response_model=int)
async def get_bed(
    use_case: IsidorBedUseCase = Depends(get_passenger_isidor_couple_use_case),
) -> int:
    return await use_case.get_bed({})
