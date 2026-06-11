from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_molly_scaler_schema import MollyScalerSchema
from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.dependencies.passenger_molly_scaler_provider import get_molly_scaler
from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerResponse

molly_scaler_router = APIRouter(prefix="/molly", tags=["molly"])


@molly_scaler_router.get("/myself")
async def introduce_myself(
    molly: MollyScalerUseCase = Depends(get_molly_scaler),
) -> MollyScalerResponse:
    return await molly.introduce_myself(
        MollyScalerSchema(
            id=9,
            name="몰리 스케일러 주인공"
        )
    )
