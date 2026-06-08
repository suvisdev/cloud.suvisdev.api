from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterResponse

class CalTesterUseCase(ABC):
    """cal_tester input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: CalTesterSchema)->CalTesterResponse:
        pass
