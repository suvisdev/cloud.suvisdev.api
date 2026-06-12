from __future__ import annotations

import logging

from fastapi.params import Depends

from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer
from titanic.dependencies.passenger_rose_model_provider import get_rose_model
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithCaptainChatCommand
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    def __init__(self, repository: SmithCaptainRepository):
        self._repository = repository
    
    
    async def chat(self, schema: ChatSchema, 
               jack: JackTrainerUseCase = Depends(get_jack_trainer),
                rose: RoseModelUseCase = Depends(get_rose_model)) -> SmithCaptainResponse:
        # Smith가 Rose(모델)를 선택하고, Jack(훈련)에게 넘긴다

        return await self._repository.chat(schema.message)
    
    
    
    async def introduce_myself(self, schemas: SmithCaptainSchema) -> SmithCaptainResponse:
        return await self._repository.introduce_myself(SmithCaptainQuery(
            id=schemas.id,
            name=schemas.name,
        ))


