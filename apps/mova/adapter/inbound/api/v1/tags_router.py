from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.tags_schema import (
    MoviesByTagSchema,
    TagCatalogSchema,
    TagCreateSchema,
    TagSchema,
)
from mova.adapter.outbound.pg.tags_pg_repository import TagsRepositoryError
from mova.app.ports.input.tags_use_case import TagsUseCase
from mova.app.use_cases.tags_interactor import TagsInteractor

tags_router = APIRouter(tags=["mova-tags"])

logger = logging.getLogger(__name__)


@tags_router.post("/tags", response_model=TagSchema, status_code=201)
async def attach_tag(req: TagCreateSchema) -> TagSchema:
    logger.info("[TagsRouter] attach — movie_id=%s %r", req.movie_id, req.label)
    use_case: TagsUseCase = TagsInteractor()
    try:
        return await use_case.attach(req)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.get("/tags/catalog", response_model=list[TagCatalogSchema])
async def list_tag_catalog(limit: int = 100) -> list[TagCatalogSchema]:
    use_case: TagsUseCase = TagsInteractor()
    try:
        return await use_case.list_catalog(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.delete("/tags/{link_id}", status_code=204)
async def unlink_tag(link_id: int) -> None:
    use_case: TagsUseCase = TagsInteractor()
    try:
        await use_case.unlink(link_id)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.get("/movies/{movie_id}/tags", response_model=list[TagSchema])
async def list_tags_by_movie(movie_id: int, limit: int = 50) -> list[TagSchema]:
    use_case: TagsUseCase = TagsInteractor()
    try:
        return await use_case.list_by_movie(movie_id, limit=limit)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@tags_router.get("/tags/{slug}/movies", response_model=list[MoviesByTagSchema])
async def list_movies_by_tag_slug(slug: str, limit: int = 50) -> list[MoviesByTagSchema]:
    use_case: TagsUseCase = TagsInteractor()
    try:
        return await use_case.list_movies_by_slug(slug, limit=limit)
    except TagsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
