from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterResponse, TestmodelResponse

class CalTesterUseCase(ABC):
    """cal_tester input port."""

    @abstractmethod
    async def get_test_model(self, test_set=None) -> TestmodelResponse:
        """잭이 훈련시킨 전략 전체를 채점해 최고점 전략을 선정."""
        pass

    @abstractmethod
    async def introduce_myself(self, schemas: CalTesterSchema)->CalTesterResponse:
        pass

    
