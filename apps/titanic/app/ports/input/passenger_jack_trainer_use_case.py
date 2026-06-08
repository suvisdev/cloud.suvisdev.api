from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema


class JackTrainerUseCase(ABC):
    """jack_trainer input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["JackTrainerSchema"]):
        pass
