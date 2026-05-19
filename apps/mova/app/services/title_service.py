import logging

from mova.app.repositories.search_stats_repository import SearchStatsRepository
from mova.app.repositories.title_repository import TitleRepository
from mova.app.schemas.title_schema import (
    MovaCastSchema,
    MovaCommentSchema,
    MovaSearchItemSchema,
    MovaTitleDetailSchema,
)

logger = logging.getLogger(__name__)


class TitleService:
    def __init__(self) -> None:
        self.title_repository = TitleRepository()
        self.search_stats_repository = SearchStatsRepository()

    async def search(self, query: str, limit: int = 12) -> list[MovaSearchItemSchema]:
        logger.info("[TitleService] search 진입 — q=%r", query)
        rows = await self.title_repository.search(query, limit=limit)

        if query.strip():
            try:
                await self.search_stats_repository.record_search(
                    query,
                    TitleRepository.to_search_matches(rows),
                )
            except Exception:
                logger.exception("[TitleService] 검색 카운트 저장 실패")

        return [
            MovaSearchItemSchema(
                id=title.slug,
                title=title.title,
                year=title.year,
                rating=title.rating,
                poster=title.poster_url,
                match_type=match_type,
            )
            for title, match_type, _person_id in rows
        ]

    async def get_detail(self, slug: str) -> MovaTitleDetailSchema | None:
        logger.info("[TitleService] get_detail 진입 — slug=%s", slug)
        title = await self.title_repository.get_by_slug(slug)
        if title is None:
            return None

        try:
            await self.search_stats_repository.record_title_view(slug)
        except Exception:
            logger.exception("[TitleService] 조회 카운트 저장 실패")

        return MovaTitleDetailSchema(
            id=title.slug,
            title=title.title,
            year=title.year,
            genres=list(title.genres or []),
            country=title.country,
            ageRating=title.age_rating,
            rankBadge=title.rank_badge,
            platform=title.platform,
            poster=title.poster_url,
            backdrop=title.backdrop_url,
            rating=title.rating,
            ratingCount=title.rating_count,
            rank=title.rank,
            badge=title.badge,
            synopsis=title.synopsis,
            ratingDistribution=list(title.rating_distribution or []),
            cast=[
                MovaCastSchema(name=p.name, role=p.role, photo=p.photo_url)
                for p in title.people
            ],
            comments=[MovaCommentSchema.model_validate(c) for c in (title.comments or [])],
            gallery=list(title.gallery or []),
        )
