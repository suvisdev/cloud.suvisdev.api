from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.dependencies.passenger_molly_scaler import get_passenger_molly_scaler_use_case

passenger_molly_scaler_router = APIRouter(prefix="/titanic/scaler", tags=["scaler"])


@passenger_molly_scaler_router.get("/scaler", response_model=int)
async def get_scaler(
    use_case: MollyScalerUseCase = Depends(get_passenger_molly_scaler_use_case),
) -> int:
    return await use_case.get_scaler({})
