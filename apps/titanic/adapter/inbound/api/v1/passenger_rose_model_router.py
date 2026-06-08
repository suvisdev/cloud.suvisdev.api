from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.passenger_rose_model_use_case import RoseDiamondUseCase
from titanic.dependencies.passenger_rose_model import get_passenger_rose_model_use_case

passenger_rose_model_router = APIRouter(prefix="/titanic/diamond", tags=["diamond"])


@passenger_rose_model_router.get("/diamond", response_model=int)
async def get_diamond(
    use_case: RoseDiamondUseCase = Depends(get_passenger_rose_model_use_case),
) -> int:
    return await use_case.get_diamond({})
