import logging
from datetime import datetime, timezone

from sqlalchemy import select, text

from database import get_engine, get_session_factory
from mova.app.models.search_stats_model import MovaSearchQuery
from mova.app.models.title_model import MovaPerson, MovaTitle

logger = logging.getLogger(__name__)


class SearchMatch:
    __slots__ = ("title_id", "match_type", "person_id")

    def __init__(self, title_id: int, match_type: str, person_id: int | None = None) -> None:
        self.title_id = title_id
        self.match_type = match_type
        self.person_id = person_id


class SearchStatsRepository:
    async def ensure_analytics_columns(self) -> None:
        """기존 Neon 테이블에 검색 카운트 컬럼이 없으면 추가한다."""
        engine = get_engine()
        statements = [
            "ALTER TABLE mova_titles ADD COLUMN IF NOT EXISTS search_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE mova_titles ADD COLUMN IF NOT EXISTS view_count INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE mova_people ADD COLUMN IF NOT EXISTS search_count INTEGER NOT NULL DEFAULT 0",
        ]
        async with engine.begin() as conn:
            for stmt in statements:
                await conn.execute(text(stmt))

    async def record_search(
        self,
        query: str,
        matches: list[SearchMatch],
    ) -> None:
        normalized = query.strip().lower()
        if not normalized:
            return

        logger.info(
            "[SearchStatsRepository] record_search — q=%r matches=%s",
            normalized,
            len(matches),
        )
        factory = get_session_factory()
        now = datetime.now(timezone.utc)

        async with factory() as session:
            existing = await session.execute(
                select(MovaSearchQuery).where(MovaSearchQuery.query == normalized),
            )
            row = existing.scalar_one_or_none()
            if row is None:
                session.add(
                    MovaSearchQuery(query=normalized, search_count=1, last_searched_at=now),
                )
            else:
                row.search_count += 1
                row.last_searched_at = now

            title_ids = {m.title_id for m in matches}
            if title_ids:
                result = await session.execute(
                    select(MovaTitle).where(MovaTitle.id.in_(title_ids)),
                )
                for title in result.scalars().all():
                    title.search_count += 1

            person_ids = {m.person_id for m in matches if m.person_id is not None}
            if person_ids:
                result = await session.execute(
                    select(MovaPerson).where(MovaPerson.id.in_(person_ids)),
                )
                for person in result.scalars().all():
                    person.search_count += 1

            await session.commit()

    async def record_title_view(self, slug: str) -> None:
        logger.info("[SearchStatsRepository] record_title_view — slug=%s", slug)
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaTitle).where(MovaTitle.slug == slug))
            title = result.scalar_one_or_none()
            if title is None:
                return
            title.view_count += 1
            await session.commit()
