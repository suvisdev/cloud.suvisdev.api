from __future__ import annotations

from mova.adapter.inbound.api.schemas.tags_schema import TagCreateSchema
from mova.app.dtos.tags_dto import MovieByTagDto, TagAttachCommand, TagCatalogDto, TagDto
from mova.app.ports.input.tags_use_case import TagsUseCase
from mova.app.ports.output.tags_repository import TagsRepository


class TagsInteractor(TagsUseCase):
    def __init__(self, repository: TagsRepository) -> None:
        self._repository = repository

    async def attach(self, payload: TagCreateSchema) -> TagDto:
        command = TagAttachCommand.from_schema(payload)
        row = await self._repository.attach(command)
        return TagDto.from_orm(row)

    async def list_catalog(self, limit: int = 100) -> list[TagCatalogDto]:
        rows = await self._repository.list_catalog(limit=limit)
        return [TagCatalogDto.from_orm(row) for row in rows]

    async def list_by_movie(self, movie_id: int, limit: int = 50) -> list[TagDto]:
        rows = await self._repository.list_by_movie(movie_id, limit=limit)
        return [TagDto.from_orm(row) for row in rows]

    async def list_movies_by_slug(
        self,
        slug: str,
        limit: int = 50,
    ) -> list[MovieByTagDto]:
        rows = await self._repository.list_movies_by_slug(slug, limit=limit)
        return [
            MovieByTagDto.from_rows(tag, movie)
            for tag, movie in rows
        ]

    async def unlink(self, link_id: int) -> None:
        await self._repository.unlink(link_id)
