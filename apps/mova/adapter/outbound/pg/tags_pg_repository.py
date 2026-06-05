from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.characters_orm import MovaCharacter
from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.orm.tags_orm import (
    TAG_KIND_CAST,
    TAG_KIND_GENRE,
    TAG_KIND_MOOD,
    TAG_KINDS,
    MovaTag,
    slugify_tag,
)
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.app.dtos.tags_dto import TagAttachCommand
from mova.app.ports.output.tags_repository import TagsRepository

logger = logging.getLogger(__name__)


class TagsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TagsPgRepository(TagsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def attach(self, command: TagAttachCommand) -> MovaTag:
        movie_id = command.movie_id
        label = command.label.strip()
        if not label:
            raise TagsRepositoryError("태그 문구가 비어 있습니다.", status_code=400)

        tag_kind = (command.tag_kind or TAG_KIND_MOOD).strip().lower()
        if tag_kind not in TAG_KINDS:
            raise TagsRepositoryError(
                f"tag_kind는 mood, genre, cast 중 하나여야 합니다. (got {tag_kind!r})",
                status_code=400,
            )

        character_id = command.character_id

        slug = str(command.slug or "").strip()
        if not slug:
            if tag_kind == TAG_KIND_CAST and character_id is not None:
                slug = f"cast-{slugify_tag(label)}"
            elif tag_kind == TAG_KIND_GENRE:
                slug = f"genre-{slugify_tag(label)}"
            else:
                slug = slugify_tag(label)
        slug = slug[:64]
        description = command.description.strip()

        if tag_kind == TAG_KIND_CAST and character_id is None:
            raise TagsRepositoryError(
                "cast 태그는 character_id(characters.id)가 필요합니다.",
                status_code=400,
            )

        logger.info(
            "[TagsPgRepository] attach — movie_id=%s kind=%s character_id=%s %r",
            movie_id,
            tag_kind,
            character_id,
            label,
        )

        async def work(session: AsyncSession) -> MovaTag:
            movie = await session.get(MovaMovie, movie_id)
            if movie is None:
                raise TagsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            if character_id is not None:
                character = await session.get(MovaCharacter, character_id)
                if character is None:
                    raise TagsRepositoryError(
                        f"연결 ID {character_id}를 찾을 수 없습니다.",
                        status_code=404,
                    )
                if character.movie_id != movie_id:
                    raise TagsRepositoryError(
                        "character_id가 해당 movie_id와 일치하지 않습니다.",
                        status_code=400,
                    )

            if character_id is not None:
                stmt = select(MovaTag).where(MovaTag.character_id == character_id)
            else:
                stmt = select(MovaTag).where(
                    MovaTag.movie_id == movie_id,
                    MovaTag.slug == slug,
                )

            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaTag(
                    movie_id=movie_id,
                    character_id=character_id,
                    tag_kind=tag_kind,
                    slug=slug,
                    label=label[:255],
                    description=description,
                )
                session.add(row)
            else:
                row.slug = slug
                row.label = label[:255]
                row.description = description
                row.tag_kind = tag_kind
                row.movie_id = movie_id

            try:
                await session.flush()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise TagsRepositoryError(
                    "영화 태그 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

        return await run_pg(self._session, work)

    async def list_catalog(self, limit: int = 100) -> list[MovaTag]:
        async def work(session: AsyncSession) -> list[MovaTag]:
            result = await session.execute(
                select(MovaTag)
                .distinct(MovaTag.slug)
                .order_by(MovaTag.slug.asc(), MovaTag.id.asc())
                .limit(limit),
            )
            return list(result.scalars().all())

        return await run_pg(self._session, work)

    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[MovaTag]:
        async def work(session: AsyncSession) -> list[MovaTag]:
            if await session.get(MovaMovie, movie_id) is None:
                raise TagsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaTag)
                .where(MovaTag.movie_id == movie_id)
                .order_by(MovaTag.tag_kind.asc(), MovaTag.label.asc())
                .limit(limit),
            )
            return list(result.scalars().all())

        return await run_pg(self._session, work)

    async def list_movies_by_slug(
        self,
        slug: str,
        limit: int = 50,
    ) -> list[tuple[MovaTag, MovaMovie]]:
        slug = slug.strip()[:64]
        if not slug:
            raise TagsRepositoryError("태그 slug가 비어 있습니다.", status_code=400)

        async def work(session: AsyncSession) -> list[tuple[MovaTag, MovaMovie]]:
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

        return await run_pg(self._session, work)

    async def unlink(self, link_id: int) -> None:
        async def work(session: AsyncSession) -> None:
            row = await session.get(MovaTag, link_id)
            if row is None:
                raise TagsRepositoryError(
                    f"태그 ID {link_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            await session.delete(row)

        await run_pg(self._session, work)
