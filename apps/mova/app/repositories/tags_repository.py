import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import get_session_factory
from mova.app.models.movies_model import MovaMovie
from mova.app.models.tags_model import MovaTag, slugify_tag

logger = logging.getLogger(__name__)


class TagsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TagsRepository:
    async def attach(self, data: dict) -> MovaTag:
        movie_id = int(data["movie_id"])
        label = str(data.get("label", "")).strip()
        if not label:
            raise TagsRepositoryError("감성 태그 문구가 비어 있습니다.", status_code=400)

        slug = str(data.get("slug") or "").strip() or slugify_tag(label)
        slug = slug[:64]
        description = str(data.get("description", "")).strip()

        logger.info("[TagsRepository] attach — movie_id=%s %r", movie_id, label)
        factory = get_session_factory()
        async with factory() as session:
            movie = await session.get(MovaMovie, movie_id)
            if movie is None:
                raise TagsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(MovaTag).where(
                    MovaTag.movie_id == movie_id,
                    MovaTag.slug == slug,
                ),
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaTag(
                    movie_id=movie_id,
                    slug=slug,
                    label=label[:255],
                    description=description,
                )
                session.add(row)
            else:
                row.label = label[:255]
                row.description = description

            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise TagsRepositoryError(
                    "영화 감성 태그 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def list_catalog(self, limit: int = 100) -> list[MovaTag]:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaTag)
                .distinct(MovaTag.slug)
                .order_by(MovaTag.slug.asc(), MovaTag.id.asc())
                .limit(limit),
            )
            return list(result.scalars().all())

    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[MovaTag]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaMovie, movie_id) is None:
                raise TagsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaTag)
                .where(MovaTag.movie_id == movie_id)
                .order_by(MovaTag.label.asc())
                .limit(limit),
            )
            return list(result.scalars().all())

    async def list_movies_by_slug(
        self,
        slug: str,
        limit: int = 50,
    ) -> list[tuple[MovaTag, MovaMovie]]:
        slug = slug.strip()[:64]
        if not slug:
            raise TagsRepositoryError("태그 slug가 비어 있습니다.", status_code=400)

        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaTag, MovaMovie)
                .join(MovaMovie, MovaTag.movie_id == MovaMovie.id)
                .where(MovaTag.slug == slug)
                .order_by(MovaMovie.title.asc())
                .limit(limit),
            )
            rows = [(row[0], row[1]) for row in result.all()]
            if not rows:
                raise TagsRepositoryError(
                    f"태그 slug '{slug}'에 해당하는 영화가 없습니다.",
                    status_code=404,
                )
            return rows

    async def unlink(self, link_id: int) -> None:
        factory = get_session_factory()
        async with factory() as session:
            row = await session.get(MovaTag, link_id)
            if row is None:
                raise TagsRepositoryError(
                    f"태그 ID {link_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            await session.delete(row)
            await session.commit()
