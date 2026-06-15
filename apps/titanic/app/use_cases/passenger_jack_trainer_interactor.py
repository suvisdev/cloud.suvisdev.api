from __future__ import annotations

import logging

from kiwipiepy import Kiwi

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository

logger = logging.getLogger(__name__)


class JackTrainerInteractor(JackTrainerUseCase):
    def __init__(self, repository: JackTrainerRepository) -> None:
        self._repository = repository
        # kiwipiepy==0.23.1 이 기능이 주입되는 곳
        self._kiwi = Kiwi()


    async def analyze_message_intent(self, user_message: str) -> dict:
        # 사용자의 질문(message)을 형태소 분석하여 키워드와 의도를 파악한다
        tokens = self._kiwi.tokenize(user_message)

        # 명사류(NNG 일반명사, NNP 고유명사) 키워드 추출
        keywords = [t.form for t in tokens if t.tag in ("NNG", "NNP", "NNB", "SL")]

        # 동사·형용사로 행위 파악
        predicates = [t.form for t in tokens if t.tag in ("VV", "VA")]

        # 질문 키워드로 의도 분류
        intent = "unknown"
        if any(k in user_message for k in ("몇", "수", "명", "얼마")):
            intent = "count_query"
        elif any(k in user_message for k in ("누구", "이름")):
            intent = "person_query"
        elif any(k in user_message for k in ("언제", "날짜", "시간")):
            intent = "time_query"
        elif any(k in user_message for k in ("어디", "장소", "위치")):
            intent = "location_query"
        elif any(k in user_message for k in ("왜", "이유")):
            intent = "reason_query"
        elif predicates:
            intent = "action_query"

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
