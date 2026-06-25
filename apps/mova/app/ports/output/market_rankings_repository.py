"""랭킹 출력 포트."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.market_rankings_dto import RankingListDto


class RankingsRepositoryPort(ABC):
    @abstractmethod
    async def get_hot(self, source: str, limit: int) -> RankingListDto:
        """HOT 랭킹 조회 (rankings → movies LEFT JOIN chat)."""
