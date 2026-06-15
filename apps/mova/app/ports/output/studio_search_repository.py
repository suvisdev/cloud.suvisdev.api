from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from mova.adapter.outbound.orm.studio_movies_orm import MovaMovie
from mova.app.dtos.studio_search_dto import StudioSearchQuery, StudioSearchResponse

MatchType = Literal["title", "person", "keyword", "synopsis"]


@dataclass(frozen=True)
class SearchHit:
    movie: MovaMovie
    match_type: MatchType


class StudioSearchRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: StudioSearchQuery) -> StudioSearchResponse:
        pass
