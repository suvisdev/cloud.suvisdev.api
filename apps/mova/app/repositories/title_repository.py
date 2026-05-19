import logging

from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from database import get_session_factory
from mova.app.models.title_model import MovaKeyword, MovaPerson, MovaTitle
from mova.app.repositories.search_stats_repository import SearchMatch

logger = logging.getLogger(__name__)


class TitleRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TitleRepository:
    async def search(self, query: str, limit: int = 12) -> list[tuple[MovaTitle, str, int | None]]:
        """작품·인물·키워드·시놉시스 검색. (title, match_type, person_id) 반환."""
        q = query.strip()
        if not q:
            return []

        logger.info("[TitleRepository] search 진입 (Neon) — q=%r limit=%s", q, limit)
        pattern = f"%{q}%"
        factory = get_session_factory()

        async with factory() as session:
            title_meta: dict[int, tuple[str, int | None]] = {}

            title_rows = await session.execute(
                select(MovaTitle).where(
                    or_(
                        MovaTitle.title.ilike(pattern),
                        MovaTitle.synopsis.ilike(pattern),
                    ),
                ).limit(limit),
            )
            for row in title_rows.scalars().all():
                match = "title" if q.lower() in row.title.lower() else "synopsis"
                title_meta[row.id] = (match, None)

            person_rows = await session.execute(
                select(MovaPerson.id, MovaPerson.title_id, MovaPerson.name).where(
                    MovaPerson.name.ilike(pattern),
                ),
            )
            for person_id, title_id, _name in person_rows.all():
                if title_id not in title_meta:
                    title_meta[title_id] = ("person", person_id)

            keyword_rows = await session.execute(
                select(MovaKeyword.title_id).where(MovaKeyword.name.ilike(pattern)),
            )
            for (title_id,) in keyword_rows.all():
                if title_id not in title_meta:
                    title_meta[title_id] = ("keyword", None)

            if not title_meta:
                return []

            ids = list(title_meta.keys())[:limit]
            result = await session.execute(select(MovaTitle).where(MovaTitle.id.in_(ids)))
            titles = {t.id: t for t in result.scalars().all()}
            return [
                (titles[i], title_meta[i][0], title_meta[i][1])
                for i in ids
                if i in titles
            ]

    async def get_by_slug(self, slug: str) -> MovaTitle | None:
        logger.info("[TitleRepository] get_by_slug 진입 (Neon) — slug=%s", slug)
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaTitle)
                .where(MovaTitle.slug == slug)
                .options(selectinload(MovaTitle.people), selectinload(MovaTitle.keywords)),
            )
            return result.scalar_one_or_none()

    async def count_titles(self) -> int:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaTitle.id))
            return len(result.all())

    @staticmethod
    def to_search_matches(
        rows: list[tuple[MovaTitle, str, int | None]],
    ) -> list[SearchMatch]:
        return [
            SearchMatch(title_id=title.id, match_type=match_type, person_id=person_id)
            for title, match_type, person_id in rows
        ]
