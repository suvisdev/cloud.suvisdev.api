import logging

from mova.app.repositories.tags_repository import TagsRepository
from mova.app.schemas.tags_schema import (
    MoviesByTagSchema,
    TagCatalogSchema,
    TagCreateSchema,
    TagSchema,
)

logger = logging.getLogger(__name__)


class TagsService:
    def __init__(self) -> None:
        self.repository = TagsRepository()

    def _tag_schema(self, row) -> TagSchema:
        return TagSchema(
            id=row.id,
            movie_id=row.movie_id,
            character_id=row.character_id,
            tag_kind=row.tag_kind or "mood",
            slug=row.slug,
            label=row.label,
            description=row.description or "",
        )

    def _catalog_schema(self, row) -> TagCatalogSchema:
        return TagCatalogSchema(
            slug=row.slug,
            label=row.label,
            description=row.description or "",
        )

    async def attach(self, payload: TagCreateSchema) -> TagSchema:
        logger.info(
            "[TagsService] attach — movie_id=%s %r",
            payload.movie_id,
            payload.label,
        )
        row = await self.repository.attach(
            {
                "movie_id": payload.movie_id,
                "label": payload.label,
                "slug": payload.slug,
                "description": payload.description,
                "character_id": payload.character_id,
                "tag_kind": payload.tag_kind,
            },
        )
        return self._tag_schema(row)

    async def list_catalog(self, limit: int = 100) -> list[TagCatalogSchema]:
        rows = await self.repository.list_catalog(limit=limit)
        return [self._catalog_schema(r) for r in rows]

    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[TagSchema]:
        rows = await self.repository.list_by_movie(movie_id, limit=limit)
        return [self._tag_schema(r) for r in rows]

    async def list_movies_by_slug(
        self,
        slug: str,
        limit: int = 50,
    ) -> list[MoviesByTagSchema]:
        rows = await self.repository.list_movies_by_slug(slug, limit=limit)
        return [
            MoviesByTagSchema(
                tag_id=tag.id,
                movie_id=movie.id,
                slug=movie.slug,
                tag_slug=tag.slug,
                tag_label=tag.label,
                title=movie.title,
                release_year=movie.release_year,
                poster=movie.poster_url,
            )
            for tag, movie in rows
        ]

    async def unlink(self, link_id: int) -> None:
        await self.repository.unlink(link_id)
