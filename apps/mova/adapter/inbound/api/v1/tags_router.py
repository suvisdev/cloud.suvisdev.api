from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from mova.adapter.inbound.api.schemas.tags_schema import (
    MoviesByTagSchema,
    TagCatalogSchema,
    TagCreateSchema,
    TagSchema,
)
from mova.adapter.outbound.pg.tags_pg_repository import TagsRepositoryError
from mova.app.ports.input.tags_use_case import TagsUseCase
from mova.dependencies.tags import get_tags_use_case

tags_router = APIRouter(tags=["mova-tags"])


@tags_router.post("/tags", response_model=TagSchema, status_code=201)
async def attach_tag(
    req: TagCreateSchema,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> TagSchema:
    try:
        return await tags.attach(req)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.get("/tags/catalog", response_model=list[TagCatalogSchema])
async def list_tag_catalog(
    limit: int = 100,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> list[TagCatalogSchema]:
    try:
        return await tags.list_catalog(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.delete("/tags/{link_id}", status_code=204)
async def unlink_tag(
    link_id: int,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> None:
    try:
        await tags.unlink(link_id)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.get("/movies/{movie_id}/tags", response_model=list[TagSchema])
async def list_tags_by_movie(
    movie_id: int,
    limit: int = 50,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> list[TagSchema]:
    try:
        return await tags.list_by_movie(movie_id, limit=limit)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.get("/tags/{slug}/movies", response_model=list[MoviesByTagSchema])
async def list_movies_by_tag_slug(
    slug: str,
    limit: int = 50,
    tags: TagsUseCase = Depends(get_tags_use_case),
) -> list[MoviesByTagSchema]:
    try:
        return await tags.list_movies_by_slug(slug, limit=limit)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
