from __future__ import annotations

from datetime import date, timedelta

from mova.adapter.inbound.api.schemas.rankings_schema import (
    HotRankingDisplaySchema,
    RankingBulkSchema,
    RankingItemCreateSchema,
)
from mova.adapter.outbound.pg.rankings_pg_repository import RankingsRepositoryError
from mova.domain.value_objects.ranking_source import (
    DEFAULT_HOT_RANKING_SOURCE,
    RANKING_SOURCE_CHAT_TREND,
    RANKING_SOURCES,
)
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.ports.output.rankings_repository import RankingsRepository


class RankingsInteractor(RankingsUseCase):
    def __init__(self, repository: RankingsRepository) -> None:
        self._repository = repository

    def _display_schema(
        self,
        ranking,
        movie,
        refined_query: str | None = None,
    ) -> HotRankingDisplaySchema:
        return HotRankingDisplaySchema(
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
            release_year=movie.release_year,
            rating=movie.rating,
            poster=movie.poster_url,
            platform=movie.platform,
            genres=list(movie.genres or []),
        )

    def _resolve_ranked_at(self, ranked_at: date | None) -> date:
        return ranked_at or date.today()

    async def save_rankings(self, payload: RankingBulkSchema) -> list[HotRankingDisplaySchema]:
        ranked_at = self._resolve_ranked_at(payload.ranked_at)
        items = [
            {
                "rank": i.rank,
                "movie_id": i.movie_id,
                "chat_id": i.chat_id,
                "score": i.score,
                "badge": i.badge,
            }
            for i in payload.items
        ]
        rows = await self._repository.replace_rankings(
            items,
            ranked_at,
            source=payload.source,
        )
        return [self._display_schema(r, m) for r, m in rows]

    async def list_hot_rankings(
        self,
        *,
        source: str,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        rows = await self._repository.list_rankings_with_movies(
            source=source,
            ranked_at=ranked_at,
            limit=limit,
        )
        return [self._display_schema(r, m, refined_query=rq) for r, m, rq in rows]

    def _parse_ranked_at(self, ranked_at: str | None) -> date | None:
        if not ranked_at:
            return None
        try:
            return date.fromisoformat(ranked_at)
        except ValueError as e:
            raise RankingsRepositoryError(
                "ranked_at 형식은 YYYY-MM-DD 입니다.",
                status_code=400,
            ) from e

    def _validate_source(self, source: str) -> str:
        if source not in RANKING_SOURCES:
            raise RankingsRepositoryError(
                f"source는 {', '.join(sorted(RANKING_SOURCES))} 중 하나여야 합니다.",
                status_code=400,
            )
        return source

    async def list_hot_rankings_from_query(
        self,
        *,
        source: str = DEFAULT_HOT_RANKING_SOURCE,
        ranked_at: str | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        return await self.list_hot_rankings(
            source=self._validate_source(source),
            ranked_at=self._parse_ranked_at(ranked_at),
            limit=limit,
        )

    async def refresh_chat_trend_rankings(
        self,
        *,
        ranked_at: date | None = None,
        window_days: int = 7,
        limit: int = 10,
    ) -> list[HotRankingDisplaySchema]:
        target_date = self._resolve_ranked_at(ranked_at)
        since = target_date - timedelta(days=max(window_days, 1))
        scores = await self._repository.aggregate_chat_trend_scores(
            since=since,
            limit=limit,
        )
        if not scores:
            return []

        items = [
            RankingItemCreateSchema(
                rank=idx,
                movie_id=row["movie_id"],
                chat_id=row["chat_id"],
                score=row["score"],
                badge="HOT" if idx == 1 else None,
            )
            for idx, row in enumerate(scores, start=1)
        ]
        return await self.save_rankings(
            RankingBulkSchema(
                ranked_at=target_date,
                source=RANKING_SOURCE_CHAT_TREND,
                items=items,
            ),
        )


__all__ = ["RankingsInteractor", "RankingsRepositoryError"]
