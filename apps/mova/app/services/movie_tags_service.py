import logging

from mova.app.repositories.movie_tags_repository import MovieTagsRepository
from mova.app.schemas.movie_tags_schema import (
    MovieTagLinkCreateSchema,
    MovieTagLinkSchema,
    MovieWithTagSchema,
    TagCreateSchema,
    TagSchema,
    TagWithMovieSchema,
)

logger = logging.getLogger(__name__)


class MovieTagsService:
    def __init__(self) -> None:
        self.repository = MovieTagsRepository()

    def _tag_schema(self, row) -> TagSchema:
        return TagSchema(
            id=row.id,
            slug=row.slug,
            label=row.label,
            description=row.description or "",
        )

    def _link_schema(self, row) -> MovieTagLinkSchema:
        return MovieTagLinkSchema(
            id=row.id,
            movie_id=row.movie_id,
            tag_id=row.tag_id,
        )

    async def save_tag(self, payload: TagCreateSchema) -> TagSchema:
        logger.info("[MovieTagsService] save_tag — %r", payload.label)
        row = await self.repository.upsert_tag(
            {
                "label": payload.label,
                "slug": payload.slug,
                "description": payload.description,
            },
        )
        return self._tag_schema(row)

    async def list_tags(self, limit: int = 100) -> list[TagSchema]:
        rows = await self.repository.list_tags(limit=limit)
        return [self._tag_schema(r) for r in rows]

    async def link(self, payload: MovieTagLinkCreateSchema) -> MovieTagLinkSchema:
        row = await self.repository.link(payload.movie_id, payload.tag_id)
        return self._link_schema(row)

    async def unlink(self, link_id: int) -> None:
        await self.repository.unlink(link_id)

    async def list_tags_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[TagSchema]:
        rows = await self.repository.list_tags_by_movie(movie_id, limit=limit)
        return [self._tag_schema(tag) for _link, tag in rows]

    async def list_movies_by_tag(
        self,
        tag_id: int,
        limit: int = 50,
    ) -> list[MovieWithTagSchema]:
        rows = await self.repository.list_movies_by_tag(tag_id, limit=limit)
        return [
            MovieWithTagSchema(
                link_id=link.id,
                movie_id=movie.id,
                tag_id=tag_id,
                slug=movie.slug,
                title=movie.title,
                release_year=movie.release_year,
                poster=movie.poster_url,
            )
            for link, movie in rows
        ]

    async def list_links_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[TagWithMovieSchema]:
        rows = await self.repository.list_tags_by_movie(movie_id, limit=limit)
        return [
            TagWithMovieSchema(
                link_id=link.id,
                movie_id=link.movie_id,
                tag_id=tag.id,
                tag_slug=tag.slug,
                tag_label=tag.label,
            )
            for link, tag in rows
        ]
