from fastapi import APIRouter, Depends

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.dependencies.passenger_rose_model_provider import get_rose_model
from titanic.app.dtos.passenger_rose_model_dto import RoseModelResponse

rose_model_router = APIRouter(prefix="/rose", tags=["rose"])


@rose_model_router.get("/myself")
async def introduce_myself(
    rose: RoseModelUseCase = Depends(get_rose_model),
) -> RoseModelResponse:
    return await rose.introduce_myself(
        RoseModelSchema(
            id=10,
            name="로즈 모델 주인공"
        )
    )
