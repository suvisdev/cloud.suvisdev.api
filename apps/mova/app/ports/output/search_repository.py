from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from mova.adapter.outbound.orm.movies_orm import MovaMovie

MatchType = Literal["title", "person", "keyword", "synopsis"]


@dataclass(frozen=True)
class SearchHit:
    movie: MovaMovie
    match_type: MatchType


class SearchRepository(ABC):
    """검색(search) 아웃바운드 포트."""

    @abstractmethod
    async def search(self, query: str, *, limit: int = 12) -> list[SearchHit]:
        pass

    @abstractmethod
    async def search_by_filters(
        self,
        filters: dict[str, Any],
        *,
        intent_type: str = "mood",
        limit: int = 12,
    ) -> list[SearchHit]:
        pass
