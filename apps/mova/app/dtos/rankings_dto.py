from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.rankings_schema import (
        HotRankingDisplaySchema,
        RankingBulkSchema,
        RankingItemCreateSchema,
    )
    from mova.adapter.outbound.orm.movies_orm import MovaMovie
    from mova.adapter.outbound.orm.rankings_orm import MovaRanking


@dataclass
class RankingItemCommand:
    rank: int
    movie_id: int
    chat_id: int | None = None
    score: int | None = None
    badge: str | None = None

    @classmethod
    def from_schema(cls, payload: RankingItemCreateSchema) -> RankingItemCommand:
        return cls(
            rank=payload.rank,
            movie_id=payload.movie_id,
            chat_id=payload.chat_id,
            score=payload.score,
            badge=payload.badge,
        )


@dataclass
class RankingBulkCommand:
    ranked_at: date | None
    source: str
    items: list[RankingItemCommand] = field(default_factory=list)

    @classmethod
    def from_schema(cls, payload: RankingBulkSchema) -> RankingBulkCommand:
        return cls(
            ranked_at=payload.ranked_at,
            source=payload.source,
            items=[RankingItemCommand.from_schema(item) for item in payload.items],
        )


@dataclass
class HotRankingDto:
    id: int
    rank: int
    movie_id: int
    chat_id: int | None
    source: str
    score: int | None
    badge: str | None
    ranked_at: date
    refined_query: str | None
    slug: str
    title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None
    genres: list[str]

    @classmethod
    def from_rows(
        cls,
        ranking: MovaRanking,
        movie: MovaMovie,
        refined_query: str | None = None,
    ) -> HotRankingDto:
        return cls(
            id=ranking.id,
            rank=ranking.rank,
            movie_id=ranking.movie_id,
            chat_id=ranking.chat_id,
            source=ranking.source,
            score=ranking.score,
            badge=ranking.badge,
            ranked_at=ranking.ranked_at,
            refined_query=refined_query,
            slug=movie.slug,
            title=movie.title,
            release_year=movie.release_year or "",
            rating=float(movie.rating or 0),
            poster=movie.poster_url or "",
            platform=movie.platform,
            genres=list(movie.genres or []),
        )

    def to_schema(self) -> HotRankingDisplaySchema:
        from mova.adapter.inbound.api.schemas.rankings_schema import HotRankingDisplaySchema

        return HotRankingDisplaySchema(
            id=self.id,
            rank=self.rank,
            movie_id=self.movie_id,
            chat_id=self.chat_id,
            source=self.source,
            score=self.score,
            badge=self.badge,
            ranked_at=self.ranked_at,
            refined_query=self.refined_query,
            slug=self.slug,
            title=self.title,
            release_year=self.release_year,
            rating=self.rating,
            poster=self.poster,
            platform=self.platform,
            genres=self.genres,
        )
