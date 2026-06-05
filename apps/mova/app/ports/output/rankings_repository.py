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
        *,
        source: str,
    ) -> list[tuple[MovaRanking, MovaMovie]]:
        pass

    @abstractmethod
    async def list_rankings_with_movies(
        self,
        *,
        source: str,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[tuple[MovaRanking, MovaMovie, str | None]]:
        pass

    @abstractmethod
    async def aggregate_chat_trend_scores(
        self,
        *,
        since: date,
        limit: int = 10,
    ) -> list[dict]:
        """picks·chat 집계 — movie_id, score, chat_id."""
        pass
