import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import get_session_factory
from mova.app.models.movie_tags_model import MovaMovieTag, MovaTag, slugify_tag
from mova.app.models.movies_model import MovaMovie

logger = logging.getLogger(__name__)


class MovieTagsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MovieTagsRepository:
    async def upsert_tag(self, data: dict) -> MovaTag:
        label = str(data.get("label", "")).strip()
        if not label:
            raise MovieTagsRepositoryError("감성 태그 문구가 비어 있습니다.", status_code=400)

        slug = str(data.get("slug") or "").strip() or slugify_tag(label)
        slug = slug[:64]

        logger.info("[MovieTagsRepository] upsert_tag — %r", label)
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaTag).where(MovaTag.slug == slug))
            row = result.scalar_one_or_none()
            if row is None:
                result = await session.execute(select(MovaTag).where(MovaTag.label == label))
                row = result.scalar_one_or_none()
            if row is None:
                row = MovaTag(
                    slug=slug,
                    label=label[:255],
                    description=str(data.get("description", "")).strip(),
                )
                session.add(row)
            else:
                row.label = label[:255]
                row.description = str(data.get("description", row.description)).strip()

            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise MovieTagsRepositoryError(
                    "감성 태그 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def get_tag(self, tag_id: int) -> MovaTag | None:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaTag).where(MovaTag.id == tag_id))
            return result.scalar_one_or_none()

    async def list_tags(self, limit: int = 100) -> list[MovaTag]:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaTag).order_by(MovaTag.label.asc()).limit(limit),
            )
            return list(result.scalars().all())

    async def link(self, movie_id: int, tag_id: int) -> MovaMovieTag:
        factory = get_session_factory()
        async with factory() as session:
            movie = await session.get(MovaMovie, movie_id)
            if movie is None:
                raise MovieTagsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            tag = await session.get(MovaTag, tag_id)
            if tag is None:
                raise MovieTagsRepositoryError(
                    f"태그 ID {tag_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(MovaMovieTag).where(
                    MovaMovieTag.movie_id == movie_id,
                    MovaMovieTag.tag_id == tag_id,
                ),
            )
            row = result.scalar_one_or_none()
            if row is not None:
                return row

            row = MovaMovieTag(movie_id=movie_id, tag_id=tag_id)
            session.add(row)
            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise MovieTagsRepositoryError(
                    "영화–감성 태그 연결에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def unlink(self, link_id: int) -> None:
        factory = get_session_factory()
        async with factory() as session:
            row = await session.get(MovaMovieTag, link_id)
            if row is None:
                raise MovieTagsRepositoryError(
                    f"연결 ID {link_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            await session.delete(row)
            await session.commit()

    async def list_tags_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[tuple[MovaMovieTag, MovaTag]]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaMovie, movie_id) is None:
                raise MovieTagsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaMovieTag, MovaTag)
                .join(MovaTag, MovaMovieTag.tag_id == MovaTag.id)
                .where(MovaMovieTag.movie_id == movie_id)
                .order_by(MovaTag.label.asc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]

    async def list_movies_by_tag(
        self,
        tag_id: int,
        limit: int = 50,
    ) -> list[tuple[MovaMovieTag, MovaMovie]]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaTag, tag_id) is None:
                raise MovieTagsRepositoryError(
                    f"태그 ID {tag_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaMovieTag, MovaMovie)
                .join(MovaMovie, MovaMovieTag.movie_id == MovaMovie.id)
                .where(MovaMovieTag.tag_id == tag_id)
                .order_by(MovaMovie.title.asc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]
