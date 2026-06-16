from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import (
    CalTesterQuery,
    CalTesterResponse,
    KaggleScoreEntry,
    TestmodelResponse,
)
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_cal_tester_repository import CalTesterRepository

logger = logging.getLogger(__name__)


class CalTesterInteractor(CalTesterUseCase):
    def __init__(self, repository: CalTesterRepository, jack: JackTrainerUseCase) -> None:
        self._repository = repository
        self._jack = jack

    async def introduce_myself(self, schemas: CalTesterSchema) -> CalTesterResponse:

        return await self._repository.introduce_myself(CalTesterQuery(
            id=schemas.id,
            name=schemas.name,
        ))
    
    async def get_test_model(self, test_set=None) -> TestmodelResponse:
        """칼이 로즈가 제안한 10개의 모델의 트레이닝 정도를 점수화 해서 1등을 뽑는것"""
        train_results = await self._jack.get_train_model()
        leaderboard = [
            KaggleScoreEntry(
                strategy=strategy_key,
                n_samples=result["n_samples"],
                accuracy=result["accuracy"],
            )
            for strategy_key, result in train_results.items()
        ]
        leaderboard.sort(key=lambda entry: entry.accuracy, reverse=True)
        return TestmodelResponse(best=leaderboard[0], leaderboard=leaderboard)
