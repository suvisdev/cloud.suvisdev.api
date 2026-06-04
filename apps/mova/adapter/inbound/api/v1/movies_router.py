from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.search_schema import MovaTitleDetailSchema
from mova.adapter.inbound.api.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)
from mova.adapter.outbound.pg.movies_pg_repository import MoviesRepositoryError
from mova.app.ports.input.movies_use_case import MoviesUseCase
from mova.app.use_cases.movies_interactor import MoviesInteractor

movies_router = APIRouter(tags=["mova-movies"])

logger = logging.getLogger(__name__)


@movies_router.get("/titles/{slug}", response_model=MovaTitleDetailSchema)
async def get_title_by_slug(slug: str) -> MovaTitleDetailSchema:
    use_case: MoviesUseCase = MoviesInteractor()
    try:
        return await use_case.get_title_by_slug(slug)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.post("/movies", response_model=MovieSchema, status_code=201)
async def save_movie(req: MovieCreateSchema) -> MovieSchema:
    logger.info("[MoviesRouter] save_movie — %r", req.title)
    use_case: MoviesUseCase = MoviesInteractor()
    try:
        return await use_case.save_movie(req)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.get("/movies", response_model=list[MovieSchema])
async def list_movies(limit: int = 100) -> list[MovieSchema]:
    use_case: MoviesUseCase = MoviesInteractor()
    try:
        return await use_case.list_movies(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.post("/movies/titles", response_model=MovieTitleSchema, status_code=201)
async def save_movie_title(req: MovieTitleCreateSchema) -> MovieTitleSchema:
    logger.info("[MoviesRouter] save_movie_title — %r", req.title)
    use_case: MoviesUseCase = MoviesInteractor()
    try:
        return await use_case.save_title(req)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.get("/movies/titles", response_model=list[MovieTitleSchema])
async def list_movie_titles(limit: int = 100) -> list[MovieTitleSchema]:
    use_case: MoviesUseCase = MoviesInteractor()
    try:
        return await use_case.list_titles(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.get("/movies/{movie_id}", response_model=MovieSchema)
async def get_movie(movie_id: int) -> MovieSchema:
    use_case: MoviesUseCase = MoviesInteractor()
    try:
        return await use_case.get_movie(movie_id)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
