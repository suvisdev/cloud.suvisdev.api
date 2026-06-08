from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.passenger_jack_trainer_use_case import JackSketchUseCase
from titanic.dependencies.passenger_jack_trainer import get_passenger_jack_trainer_use_case

passenger_jack_trainer_router = APIRouter(prefix="/titanic/sketch", tags=["sketch"])


@passenger_jack_trainer_router.get("/sketch", response_model=int)
async def get_sketch(
    use_case: JackSketchUseCase = Depends(get_passenger_jack_trainer_use_case),
) -> int:
    return await use_case.get_sketch({})
