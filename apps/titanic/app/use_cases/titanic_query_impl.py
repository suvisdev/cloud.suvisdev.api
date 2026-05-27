from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from titanic.app.use_cases.jack_service import JackService

logger = logging.getLogger(__name__)


class TitanicQueryImpl:
    """타이타닉 조회 유스케이스 — 애플리케이션 서비스에 위임."""

    def __init__(self, service: JackService | None = None) -> None:
        self._service = service or JackService()

    def get_data(self) -> pd.DataFrame:
        return self._service.get_data()

    def get_count(self) -> int:
        return self._service.get_count()

    def get_survived_count(self) -> int:
        return self._service.get_survived_count()

    def get_dead_count(self) -> int:
        return self._service.get_dead_count()

    def has_decision_tree_model(self) -> bool:
        return self._service.has_decision_tree_model()

    def get_model_name_and_accuracy(self) -> dict[str, str | None]:
        return self._service.get_model_name_and_accuracy()

    def analyze_dicaprio_survival(self) -> dict[str, Any]:
        logger.info("[TitanicQueryImpl] 디카프리오 생존 통계 분석 요청")
        return self._service.analyze_dicaprio_survival()
