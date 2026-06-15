from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.platform_assistants_dto import PlatformAssistantsQuery, PlatformAssistantsResponse


class PlatformAssistantsRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: PlatformAssistantsQuery) -> PlatformAssistantsResponse:
        pass
