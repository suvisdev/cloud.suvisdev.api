from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_molly_scaler_schema import MollyScalerSchema


class MollyScalerUseCase(ABC):
    """molly_scaler input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["MollyScalerSchema"]):
        pass
