from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from mova.adapter.inbound.api.schemas.rankings_schema import (
    HotRankingDisplaySchema,
    RankingBulkSchema,
)


class RankingsUseCase(ABC):
    @abstractmethod
    async def save_rankings(self, payload: RankingBulkSchema) -> list[HotRankingDisplaySchema]:
        pass

    @abstractmethod
    async def list_hot_rankings(
        self,
        *,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        pass
