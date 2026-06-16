from __future__ import annotations

import logging

from fastapi.params import Depends

from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import ChatSchema, SmithCaptainSchema
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithCaptainChatCommand, SmithChatResponse
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.crew_smith_captain_repository import SmithCaptainRepository
from titanic.dependencies.passenger_cal_tester_provider import get_cal_tester_use_case
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_trainer_use_case
from titanic.dependencies.crew_walter_roaster_provider import get_walter_roaster_use_case
from titanic.dependencies.passenger_rose_model_provider import get_rose_model_use_case

logger = logging.getLogger(__name__)


class SmithCaptainInteractor(SmithCaptainUseCase):
    def __init__(self, repository: SmithCaptainRepository,
                 jack: JackTrainerUseCase,
                 rose: RoseModelUseCase,
                 cal: CalTesterUseCase,
                 walter: WalterUseCase):
        self._repository = repository
        self.jack = jack
        self.rose = rose
        self.cal = cal
        self.walter = walter

    async def chat(self, schema: ChatSchema) -> SmithChatResponse:
        
        # schema 내용 로그로 출력
        logger.info(f"[SmithCaptainInteractor] chat | schema={schema.json()}")
        train_set = self.walter.get_train_set()
        test_set = self.walter.get_test_set()
        self.jack.train_model(train_set)
        self.cal.test_model(test_set)
    

        return "1309명이야"
    
    
    
    async def introduce_myself(self, schemas: SmithCaptainSchema) -> SmithCaptainResponse:
        return await self._repository.introduce_myself(SmithCaptainQuery(
            id=schemas.id,
            name=schemas.name,
        ))


