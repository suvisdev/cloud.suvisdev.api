from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.passenger_cal_tester_use_case import CalPistolUseCase
from titanic.dependencies.passenger_cal_tester import get_passenger_cal_tester_use_case

passenger_cal_tester_router = APIRouter(prefix="/titanic/pistol", tags=["pistol"])


@passenger_cal_tester_router.get("/pistol")
async def get_pistol(
    use_case: CalPistolUseCase = Depends(get_passenger_cal_tester_use_case),
) -> None:
    return await use_case.get_pistol({})
