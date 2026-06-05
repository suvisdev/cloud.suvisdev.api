from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema
    from mova.adapter.outbound.orm.movies_orm import MovaMovie
    from mova.app.ports.output.search_repository import SearchHit

MatchType = Literal["title", "person", "keyword", "synopsis"]


@dataclass
class SearchIntentQuery:
    refined_query: str
    keywords: list[str] = field(default_factory=list)
    intent_type: str = "mood"
    search_filters: dict[str, Any] = field(default_factory=dict)
    limit: int = 12


@dataclass
class SearchItemDto:
    id: str
    title: str
    year: str
    rating: float
    poster: str
    match_type: MatchType

    @classmethod
    def from_hit(cls, hit: SearchHit, *, slug: str) -> SearchItemDto:
        movie: MovaMovie = hit.movie
        return cls(
            id=slug,
            title=movie.title,
            year=movie.release_year or "",
            rating=float(movie.rating or 0),
            poster=movie.poster_url or "",
            match_type=hit.match_type,
        )

    def to_schema(self) -> MovaSearchItemSchema:
        from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema

        return MovaSearchItemSchema(
            id=self.id,
            title=self.title,
            year=self.year,
            rating=self.rating,
            poster=self.poster,
            match_type=self.match_type,
        )
