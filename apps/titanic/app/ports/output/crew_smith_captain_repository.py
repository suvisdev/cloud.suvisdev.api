from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithCaptainChatCommand


class SmithCaptainRepository(ABC):
    """crew_smith_captain output port."""
    
    @abstractmethod
    async def chat(self, command: SmithCaptainChatCommand) -> SmithCaptainResponse:
        pass

    @abstractmethod
    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        pass

