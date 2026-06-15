from __future__ import annotations

from mova.adapter.inbound.api.schemas.studio_movies_schema import StudioMoviesSchema
from mova.app.dtos.studio_movies_dto import StudioMoviesQuery, StudioMoviesResponse
from mova.app.ports.input.studio_movies_use_case import StudioMoviesUseCase
from mova.app.ports.output.studio_movies_repository import StudioMoviesRepository


class StudioMoviesInteractor(StudioMoviesUseCase):
    def __init__(self, repository: StudioMoviesRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: StudioMoviesSchema) -> StudioMoviesResponse:
        return await self._repository.introduce_myself(StudioMoviesQuery(
            id=schemas.id,
            name=schemas.name,
        ))
