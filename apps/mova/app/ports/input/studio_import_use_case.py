from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.studio_import_schema import StudioImportSchema
from mova.app.dtos.studio_import_dto import StudioImportResponse


class StudioImportUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: StudioImportSchema) -> StudioImportResponse:
        pass
