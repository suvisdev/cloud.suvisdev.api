from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse

class JackTrainerUseCase(ABC):
    """jack_trainer input port."""
   
    @abstractmethod
    async def get_train_model(self, train_set=None) -> dict[str, Any]:
        '''로즈가 제안한 모델들을 훈련시키는 메소드'''


    @abstractmethod
    async def introduce_myself(self, schemas: JackTrainerSchema)->JackTrainerResponse:
        pass
    


    