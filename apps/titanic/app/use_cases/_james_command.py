from __future__ import annotations

import logging

from titanic.app.use_cases.caledon_validation import TitanicPredictInput, TitanicPredictOutput
from titanic.app.use_cases.jack_service import JackService

logger = logging.getLogger(__name__)


class TitanicCommandImpl:
    """타이타닉 명령 유스케이스 — 생존 예측 등 쓰기/연산 작업."""

    def __init__(self, service: JackService | None = None) -> None:
        self._service = service or JackService()

    def predict(self, payload: TitanicPredictInput) -> TitanicPredictOutput:
        logger.info(
            "[TitanicCommandImpl] 생존 예측 — Pclass=%s Sex=%s Age=%s",
            payload.pclass,
            payload.sex,
            payload.age,
        )
        return self._service.predict_survival(payload)
