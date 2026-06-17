from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse


class JackTrainerUseCase(ABC):

    @abstractmethod
    async def train_model(self, train_set: pd.DataFrame, test_set: pd.DataFrame | None = None) -> dict[str, Any]:
        '''로즈가 제안한 모델들을 훈련시키고 test_set도 전처리해서 반환하는 메소드'''
        pass

    @abstractmethod
    async def introduce_myself(self, schema: JackTrainerSchema) -> JackTrainerResponse:
        pass
