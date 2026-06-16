from __future__ import annotations

import logging
from typing import Any

from kiwipiepy import Kiwi

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelTrainSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository

logger = logging.getLogger(__name__)


class JackTrainerInteractor(JackTrainerUseCase):
    def __init__(self, repository: JackTrainerRepository, rose: RoseModelUseCase) -> None:
        self._repository = repository
        self._rose = rose
        # kiwipiepy==0.23.1 이 기능이 주입되는 곳
        self._kiwi = Kiwi()


    async def get_train_model(self, train_set=None) -> dict[str, Any]:
        '''로즈가 제안한 모델들을 훈련시키는 메소드'''
        results: dict[str, Any] = {}
        for strategy_key in await self._rose.list_strategies():
            response = await self._rose.train(RoseModelTrainSchema(strategy=strategy_key))
            results[strategy_key] = {
                "n_samples": response.n_samples,
                "accuracy": response.accuracy,
            }

        return results


    async def analyze_message_intent(self, user_message: str) -> dict:
        # 사용자의 질문(message)을 형태소 분석하여 키워드와 의도를 파악한다
        tokens = self._kiwi.tokenize(user_message)

        # 명사류(NNG 일반명사, NNP 고유명사) 키워드 추출
        keywords = [t.form for t in tokens if t.tag in ("NNG", "NNP", "NNB", "SL")]

        # 동사·형용사로 행위 파악
        predicates = [t.form for t in tokens if t.tag in ("VV", "VA")]

        # 질문 키워드로 의도 분류
        intent_rules: tuple[tuple[tuple[str, ...], str], ...] = (
            (("몇", "수", "명", "얼마"), "count_query"),
            (("누구", "이름"), "person_query"),
            (("언제", "날짜", "시간"), "time_query"),
            (("어디", "장소", "위치"), "location_query"),
            (("왜", "이유"), "reason_query"),
        )
        intent = next(
            (label for keys, label in intent_rules if any(k in user_message for k in keys)),
            "action_query" if predicates else "unknown",
        )

        logger.info(
            "[JackTrainerInteractor] analyze_message_intent | keywords=%s intent=%s",
            keywords, intent,
        )
        return {"keywords": keywords, "predicates": predicates, "intent": intent}





    async def introduce_myself(self, schemas: JackTrainerSchema) -> JackTrainerResponse:
    
        return await self._repository.introduce_myself(JackTrainerQuery(
            id=schemas.id,
            name=schemas.name,
        ))
