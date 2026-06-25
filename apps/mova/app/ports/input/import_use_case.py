from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.studio_import_dto import StudioImportQuery, StudioImportResponse


class ImportUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, query: StudioImportQuery) -> StudioImportResponse:
        pass
