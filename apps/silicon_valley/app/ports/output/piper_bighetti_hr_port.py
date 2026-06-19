from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse

class BighettiHrPort(ABC):
    """piper_bighetti_hr output port."""

    @abstractmethod
    def introduce_myself(self, query: BighettiHrQuery)->BighettiHrResponse:
        pass
