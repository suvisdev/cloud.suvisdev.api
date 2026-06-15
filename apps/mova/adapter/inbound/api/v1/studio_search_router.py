from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.studio_search_schema import StudioSearchSchema
from mova.app.dtos.studio_search_dto import StudioSearchResponse
from mova.app.ports.input.studio_search_use_case import StudioSearchUseCase
from mova.dependencies.studio_search_provider import get_studio_search_use_case

studio_search_router = APIRouter(prefix="/search", tags=["mova-search"])


@studio_search_router.get("/myself")
async def introduce_myself(
    search: StudioSearchUseCase = Depends(get_studio_search_use_case),
) -> StudioSearchResponse:
    return await search.introduce_myself(
        StudioSearchSchema(id=1, name="검색 감독 (Search Director)")
    )
