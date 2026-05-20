import logging

from mova.app.schemas.mova_title_schema import MovaTitleDetailSchema
from mova.app.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)
from mova.app.services.movies_service import MoviesService

logger = logging.getLogger(__name__)


class MoviesController:
    def __init__(self) -> None:
        self.movies_service = MoviesService()

    async def save_movie(self, payload: MovieCreateSchema) -> MovieSchema:
        logger.info("[MoviesController] save_movie — %r", payload.title)
        return await self.movies_service.save_movie(payload)

    async def save_title(self, payload: MovieTitleCreateSchema) -> MovieTitleSchema:
        logger.info("[MoviesController] save_title — %r", payload.title)
        return await self.movies_service.save_title(payload)

    async def list_movies(self, limit: int = 100) -> list[MovieSchema]:
        return await self.movies_service.list_movies(limit=limit)

    async def list_titles(self, limit: int = 100) -> list[MovieTitleSchema]:
        return await self.movies_service.list_titles(limit=limit)

    async def get_movie(self, movie_id: int) -> MovieSchema:
        return await self.movies_service.get_movie(movie_id)

    async def get_title_by_slug(self, slug: str) -> MovaTitleDetailSchema:
        logger.info("[MoviesController] get_title_by_slug — %r", slug)
        return await self.movies_service.get_title_by_slug(slug)
