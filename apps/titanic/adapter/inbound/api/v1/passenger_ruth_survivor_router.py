from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthCorsetUseCase
from titanic.dependencies.passenger_ruth_survivor import get_passenger_ruth_survivor_use_case

passenger_ruth_survivor_router = APIRouter(prefix="/titanic/corset", tags=["corset"])


@passenger_ruth_survivor_router.get("/corset", response_model=int)
async def get_corset(
    use_case: RuthCorsetUseCase = Depends(get_passenger_ruth_survivor_use_case),
) -> int:
    return await use_case.get_corset({})
