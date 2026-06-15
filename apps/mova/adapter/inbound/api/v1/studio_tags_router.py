from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.studio_tags_schema import StudioTagsSchema
from mova.app.dtos.studio_tags_dto import StudioTagsResponse
from mova.app.ports.input.studio_tags_use_case import StudioTagsUseCase
from mova.dependencies.studio_tags_provider import get_studio_tags_use_case

studio_tags_router = APIRouter(prefix="/tags", tags=["mova-tags"])


@studio_tags_router.get("/myself")
async def introduce_myself(
    tags: StudioTagsUseCase = Depends(get_studio_tags_use_case),
) -> StudioTagsResponse:
    return await tags.introduce_myself(
        StudioTagsSchema(id=1, name="홍보 담당자 (Publicist)")
    )
