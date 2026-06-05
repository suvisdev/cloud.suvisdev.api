from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.chat_orm import MovaChat
from mova.app.dtos.chat_dto import ChatUpsertCommand


class ChatRepository(ABC):
    @abstractmethod
    async def upsert(self, command: ChatUpsertCommand) -> int:
        pass

    @abstractmethod
    async def get_top_for_context(
        self,
        limit: int = 6,
        *,
        user_id: int | None = None,
    ) -> list[MovaChat]:
        pass
