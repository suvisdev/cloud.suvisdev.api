from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.chat_orm import MovaChat


class ChatRepository(ABC):
    @abstractmethod
    async def upsert(
        self,
        raw_message: str,
        refined_query: str,
        keywords: list[str] | None = None,
        *,
        intent_type: str = "mood",
        search_filters: dict | None = None,
        user_id: int | None = None,
        assistant_id: int | None = None,
    ) -> int:
        pass

    @abstractmethod
    async def get_top_for_context(
        self,
        limit: int = 6,
        *,
        user_id: int | None = None,
    ) -> list[MovaChat]:
        pass
