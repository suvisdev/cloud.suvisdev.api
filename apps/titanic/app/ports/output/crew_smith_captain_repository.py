from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse

class SmithCaptainRepository(ABC):
    """crew_smith_captain output port."""

    @abstractmethod
    def introduce_myself(self, query: SmithCaptainQuery)->SmithCaptainResponse:
        pass
