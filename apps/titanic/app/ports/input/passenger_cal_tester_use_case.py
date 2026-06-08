from __future__ import annotations

from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema


class CalTesterUseCase(ABC):
    """cal_tester input port."""

    @abstractmethod
    async def introduce_myself(self, schemas: list["CalTesterSchema"]):
        pass
