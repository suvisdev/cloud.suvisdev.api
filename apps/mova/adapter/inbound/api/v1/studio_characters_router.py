from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.studio_characters_schema import StudioCharactersSchema
from mova.app.dtos.studio_characters_dto import StudioCharactersResponse
from mova.app.ports.input.studio_characters_use_case import StudioCharactersUseCase
from mova.dependencies.studio_characters_provider import get_studio_characters_use_case

studio_characters_router = APIRouter(prefix="/characters", tags=["mova-characters"])


@studio_characters_router.get("/myself")
async def introduce_myself(
    characters: StudioCharactersUseCase = Depends(get_studio_characters_use_case),
) -> StudioCharactersResponse:
    return await characters.introduce_myself(
        StudioCharactersSchema(id=1, name="캐스팅 감독 (Casting Director)")
    )
