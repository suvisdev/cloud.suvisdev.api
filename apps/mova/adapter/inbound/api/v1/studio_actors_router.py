from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.studio_actors_schema import StudioActorsSchema
from mova.app.dtos.studio_actors_dto import StudioActorsResponse
from mova.app.ports.input.studio_actors_use_case import StudioActorsUseCase
from mova.dependencies.studio_actors_provider import get_studio_actors_use_case

studio_actors_router = APIRouter(prefix="/actors", tags=["mova-actors"])


@studio_actors_router.get("/myself")
async def introduce_myself(
    actors: StudioActorsUseCase = Depends(get_studio_actors_use_case),
) -> StudioActorsResponse:
    return await actors.introduce_myself(
        StudioActorsSchema(id=1, name="배우 (Actor)")
    )
