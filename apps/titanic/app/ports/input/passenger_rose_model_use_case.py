from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelResponse

class RoseModelUseCase(ABC):
    """rose_model input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: RoseModelSchema)->RoseModelResponse:
        pass
