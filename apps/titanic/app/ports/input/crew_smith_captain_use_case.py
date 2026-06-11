from __future__ import annotations

from abc import ABC, abstractmethod

from suvisdev.apps.titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse
from suvisdev.apps.titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from suvisdev.apps.titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema


class SmithCaptainUseCase(ABC):
    """smith_captain input port."""

    @abstractmethod
    async def chat(self, schema: ChatSchema) -> SmithCaptainResponse:
        pass


    @abstractmethod
    async def introduce_myself(self, schemas: SmithCaptainSchema, 
                               jack: JackTrainerUseCase, 
                               rose: RoseModelUseCase) -> SmithCaptainResponse:
        pass

