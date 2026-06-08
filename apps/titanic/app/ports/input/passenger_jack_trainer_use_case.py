from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse

class JackTrainerUseCase(ABC):
    """jack_trainer input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: JackTrainerSchema)->JackTrainerResponse:
        pass
