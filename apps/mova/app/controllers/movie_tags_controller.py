import logging

from mova.app.schemas.movie_tags_schema import (
    MovieTagLinkCreateSchema,
    MovieTagLinkSchema,
    MovieWithTagSchema,
    TagCreateSchema,
    TagSchema,
    TagWithMovieSchema,
)
from mova.app.services.movie_tags_service import MovieTagsService

logger = logging.getLogger(__name__)


class MovieTagsController:
    def __init__(self) -> None:
        self.service = MovieTagsService()

    async def save_tag(self, payload: TagCreateSchema) -> TagSchema:
        logger.info("[MovieTagsController] save_tag — %r", payload.label)
        return await self.service.save_tag(payload)

    async def list_tags(self, limit: int = 100) -> list[TagSchema]:
        return await self.service.list_tags(limit=limit)

    async def link(self, payload: MovieTagLinkCreateSchema) -> MovieTagLinkSchema:
        logger.info(
            "[MovieTagsController] link — movie_id=%s tag_id=%s",
            payload.movie_id,
            payload.tag_id,
        )
        return await self.service.link(payload)

    async def unlink(self, link_id: int) -> None:
        await self.service.unlink(link_id)

    async def list_tags_by_movie(self, movie_id: int, limit: int = 50) -> list[TagSchema]:
        return await self.service.list_tags_by_movie(movie_id, limit=limit)

    async def list_movies_by_tag(self, tag_id: int, limit: int = 50) -> list[MovieWithTagSchema]:
        return await self.service.list_movies_by_tag(tag_id, limit=limit)

    async def list_links_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[TagWithMovieSchema]:
        return await self.service.list_links_by_movie(movie_id, limit=limit)
