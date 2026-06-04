from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.orm.rankings_orm import MovaRanking


class RankingsRepository(ABC):
    @abstractmethod
    async def replace_rankings(
        self,
        items: list[dict],
        ranked_at: date,
    ) -> list[tuple[MovaRanking, MovaMovie]]:
        pass

    @abstractmethod
    async def list_rankings_with_movies(
        self,
        *,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[tuple[MovaRanking, MovaMovie]]:
        pass
