import logging

from mova.app.schemas.tags_schema import (
    MoviesByTagSchema,
    TagCatalogSchema,
    TagCreateSchema,
    TagSchema,
)
from mova.app.services.tags_service import TagsService

logger = logging.getLogger(__name__)


class TagsController:
    def __init__(self) -> None:
        self.service = TagsService()

    async def attach(self, payload: TagCreateSchema) -> TagSchema:
        logger.info(
            "[TagsController] attach — movie_id=%s %r",
            payload.movie_id,
            payload.label,
        )
        return await self.service.attach(payload)

    async def list_catalog(self, limit: int = 100) -> list[TagCatalogSchema]:
        return await self.service.list_catalog(limit=limit)

    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[TagSchema]:
        return await self.service.list_by_movie(movie_id, limit=limit)

    async def list_movies_by_slug(
        self,
        slug: str,
        limit: int = 50,
    ) -> list[MoviesByTagSchema]:
        return await self.service.list_movies_by_slug(slug, limit=limit)

    async def unlink(self, link_id: int) -> None:
        await self.service.unlink(link_id)
