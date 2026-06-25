from __future__ import annotations

from mova.app.dtos.studio_import_dto import StudioImportQuery, StudioImportResponse
from mova.app.ports.input.import_use_case import ImportUseCase
from mova.app.ports.output.movies_repository import MoviesRepositoryPort


class ImportInteractor(ImportUseCase):
    def __init__(self, repository: MoviesRepositoryPort) -> None:
        self._repository = repository

    async def introduce_myself(self, query: StudioImportQuery) -> StudioImportResponse:
        return await self._repository.introduce_myself(query)
