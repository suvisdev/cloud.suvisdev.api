from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_ruth_validation_schema import RuthValidationSchema


class RuthValidationUseCase(ABC):
    """ruth_validation input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["RuthValidationSchema"]):
        pass
