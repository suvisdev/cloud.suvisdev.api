from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from mova.adapter.inbound.api.schemas.rankings_schema import (
    HotRankingDisplaySchema,
    RankingBulkSchema,
)
from mova.domain.value_objects.ranking_source import DEFAULT_HOT_RANKING_SOURCE


class RankingsUseCase(ABC):
    @abstractmethod
    async def save_rankings(self, payload: RankingBulkSchema) -> list[HotRankingDisplaySchema]:
        pass

    @abstractmethod
    async def list_hot_rankings(
        self,
        *,
        source: str,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        pass

    @abstractmethod
    async def list_hot_rankings_from_query(
        self,
        *,
        source: str = DEFAULT_HOT_RANKING_SOURCE,
        ranked_at: str | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        pass

    @abstractmethod
    async def refresh_chat_trend_rankings(
        self,
        *,
        ranked_at: date | None = None,
        window_days: int = 7,
        limit: int = 10,
    ) -> list[HotRankingDisplaySchema]:
        pass
