from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.studio_movies_schema import StudioMoviesSchema
from mova.app.dtos.studio_movies_dto import StudioMoviesResponse
from mova.app.ports.input.studio_movies_use_case import StudioMoviesUseCase
from mova.dependencies.studio_movies_provider import get_studio_movies_use_case

studio_movies_router = APIRouter(prefix="/movies", tags=["mova-movies"])


@studio_movies_router.get("/myself")
async def introduce_myself(
    movies: StudioMoviesUseCase = Depends(get_studio_movies_use_case),
) -> StudioMoviesResponse:
    return await movies.introduce_myself(
        StudioMoviesSchema(id=1, name="감독 (Director)")
    )
