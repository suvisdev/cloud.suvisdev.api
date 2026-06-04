from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRecommendationSchema


class PicksRepository(ABC):
    @abstractmethod
    async def save_chat_recommendations(
        self,
        *,
        chat_id: int,
        user_id: int | None,
        movie_ids: list[tuple[int, MovaChatRecommendationSchema, int]],
    ) -> int:
        pass
