from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from mova.adapter.inbound.api.schemas.search_schema import MovaTitleDetailSchema
from mova.adapter.inbound.api.schemas.movies_schema import (
    MovieCreateSchema,
    MovieSchema,
    MovieTitleCreateSchema,
    MovieTitleSchema,
)
from mova.adapter.outbound.pg.movies_pg_repository import MoviesRepositoryError
from mova.app.ports.input.movies_use_case import MoviesUseCase
from mova.dependencies.movies import get_movies_use_case

movies_router = APIRouter(tags=["mova-movies"])


@movies_router.get("/titles/{slug}", response_model=MovaTitleDetailSchema)
async def get_title_by_slug(
    slug: str,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> MovaTitleDetailSchema:
    try:
        return await movies.get_title_by_slug(slug)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.post("/movies", response_model=MovieSchema, status_code=201)
async def save_movie(
    req: MovieCreateSchema,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> MovieSchema:
    try:
        return await movies.save_movie(req)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.get("/movies", response_model=list[MovieSchema])
async def list_movies(
    limit: int = 100,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> list[MovieSchema]:
    try:
        return await movies.list_movies(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.post("/movies/titles", response_model=MovieTitleSchema, status_code=201)
async def save_movie_title(
    req: MovieTitleCreateSchema,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> MovieTitleSchema:
    try:
        return await movies.save_title(req)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.get("/movies/titles", response_model=list[MovieTitleSchema])
async def list_movie_titles(
    limit: int = 100,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> list[MovieTitleSchema]:
    try:
        return await movies.list_titles(limit=limit)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movies_router.get("/movies/{movie_id}", response_model=MovieSchema)
async def get_movie(
    movie_id: int,
    movies: MoviesUseCase = Depends(get_movies_use_case),
) -> MovieSchema:
    try:
        return await movies.get_movie(movie_id)
    except MoviesRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
