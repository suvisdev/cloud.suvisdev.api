from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterResponse

class CalTesterRepository(ABC):
    """passenger_cal_tester output port."""

    @abstractmethod
    def introduce_myself(self, query: CalTesterQuery)->CalTesterResponse:
        pass
