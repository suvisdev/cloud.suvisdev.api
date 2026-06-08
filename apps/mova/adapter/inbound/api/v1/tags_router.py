from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.http_errors import invoke
from mova.adapter.inbound.api.schemas.tags_schema import (
    MoviesByTagSchema,
    TagCatalogSchema,
    TagCreateSchema,
    TagSchema,
)
from mova.adapter.outbound.pg.tags_pg_repository import TagsRepositoryError
from mova.app.ports.input.tags_use_case import TagsUseCase
from mova.dependencies.tags_provider import get_tags_use_case

tags_router = APIRouter(tags=["mova-tags"])
_REPO_ERRORS = (TagsRepositoryError,)


@tags_router.post("/tags", response_model=TagSchema, status_code=201)
async def attach_tag(
    req: TagCreateSchema,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> TagSchema:
    return (await invoke(tags.attach(req), domain_errors=_REPO_ERRORS)).to_schema()


@tags_router.get("/tags/catalog", response_model=list[TagCatalogSchema])
async def list_tag_catalog(
    limit: int = 100,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> list[TagCatalogSchema]:
    rows = await invoke(tags.list_catalog(limit=limit))
    return [row.to_schema() for row in rows]


@tags_router.delete("/tags/{link_id}", status_code=204)
async def unlink_tag(
    link_id: int,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> None:
    await invoke(tags.unlink(link_id), domain_errors=_REPO_ERRORS)


@tags_router.get("/movies/{movie_id}/tags", response_model=list[TagSchema])
async def list_tags_by_movie(
    movie_id: int,
    limit: int = 50,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> list[TagSchema]:
    rows = await invoke(tags.list_by_movie(movie_id, limit=limit), domain_errors=_REPO_ERRORS)
    return [row.to_schema() for row in rows]


@tags_router.get("/tags/{slug}/movies", response_model=list[MoviesByTagSchema])
async def list_movies_by_tag_slug(
    slug: str,
    limit: int = 50,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> list[MoviesByTagSchema]:
    rows = await invoke(tags.list_movies_by_slug(slug, limit=limit), domain_errors=_REPO_ERRORS)
    return [row.to_schema() for row in rows]
