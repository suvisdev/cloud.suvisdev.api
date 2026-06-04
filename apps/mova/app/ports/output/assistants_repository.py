from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.assistants_orm import MovaAssistant


class AssistantsRepository(ABC):
    @abstractmethod
    async def get_by_slug(self, slug: str) -> MovaAssistant | None:
        pass

    @abstractmethod
    async def get_default(self) -> MovaAssistant | None:
        pass
