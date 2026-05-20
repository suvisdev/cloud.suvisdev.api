import logging
from datetime import date

from mova.app.repositories.rankings_repository import RankingsRepository
from mova.app.schemas.rankings_schema import (
    HotRankingDisplaySchema,
    RankingBulkSchema,
    RankingItemCreateSchema,
    RankingItemSchema,
)

logger = logging.getLogger(__name__)


class RankingsService:
    def __init__(self) -> None:
        self.rankings_repository = RankingsRepository()

    def _ranking_schema(self, ranking, movie) -> RankingItemSchema:
        return RankingItemSchema(
            id=ranking.id,
            rank=ranking.rank,
            movie_id=ranking.movie_id,
            badge=ranking.badge,
            ranked_at=ranking.ranked_at,
        )

    def _display_schema(self, ranking, movie) -> HotRankingDisplaySchema:
        return HotRankingDisplaySchema(
            id=ranking.id,
            rank=ranking.rank,
            movie_id=ranking.movie_id,
            badge=ranking.badge,
            ranked_at=ranking.ranked_at,
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
        logger.info(
            "[RankingsService] save_rankings — date=%s count=%s",
            ranked_at,
            len(payload.items),
        )
        items = [
            {
                "rank": i.rank,
                "movie_id": i.movie_id,
                "badge": i.badge,
            }
            for i in payload.items
        ]
        rows = await self.rankings_repository.replace_rankings(items, ranked_at)
        return [self._display_schema(r, m) for r, m in rows]

    async def list_hot_rankings(
        self,
        *,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[HotRankingDisplaySchema]:
        rows = await self.rankings_repository.list_rankings_with_movies(
            ranked_at=ranked_at,
            limit=limit,
        )
        return [self._display_schema(r, m) for r, m in rows]
