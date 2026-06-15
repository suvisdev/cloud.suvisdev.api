from __future__ import annotations

from mova.adapter.inbound.api.schemas.studio_import_schema import StudioImportSchema
from mova.app.dtos.studio_import_dto import StudioImportQuery, StudioImportResponse
from mova.app.ports.input.studio_import_use_case import StudioImportUseCase
from mova.app.ports.output.studio_movies_repository import StudioMoviesRepository


class StudioImportInteractor(StudioImportUseCase):
    def __init__(self, repository: StudioMoviesRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: StudioImportSchema) -> StudioImportResponse:
        return await self._repository.introduce_myself(StudioImportQuery(
            id=schemas.id,
            name=schemas.name,
        ))
