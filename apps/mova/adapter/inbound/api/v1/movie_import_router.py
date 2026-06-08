from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.movie_import_schema import MovieImportResultSchema
from mova.app.ports.input.movie_import_use_case import MovieImportUseCase
from mova.dependencies.movie_import_provider import get_movie_import_use_case

movie_import_router = APIRouter(tags=["mova-import"])


@movie_import_router.post("/import/tmdb/popular", response_model=MovieImportResultSchema)
async def import_tmdb_popular(
    pages: int = 2,
    setup_rankings: bool = True,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (
        await movie_import.import_popular(pages=pages, setup_rankings=setup_rankings)
    ).to_schema()


@movie_import_router.post("/import/tmdb/search", response_model=MovieImportResultSchema)
async def import_tmdb_search(
    q: str,
    pages: int = 1,
    setup_rankings: bool = False,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (
        await movie_import.import_search(q, pages=pages, setup_rankings=setup_rankings)
    ).to_schema()


@movie_import_router.post("/import/tmdb/movie/{tmdb_id}", response_model=MovieImportResultSchema)
async def import_tmdb_movie(
    tmdb_id: int,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (await movie_import.import_by_tmdb_id(tmdb_id)).to_schema()


@movie_import_router.post("/import/kofic/daily", response_model=MovieImportResultSchema)
async def import_kofic_daily(
    target_date: str | None = None,
    setup_rankings: bool = True,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (
        await movie_import.import_kofic_daily(
            target_date=target_date,
            setup_rankings=setup_rankings,
        )
    ).to_schema()


@movie_import_router.post("/import/kofic/weekly", response_model=MovieImportResultSchema)
async def import_kofic_weekly(
    target_date: str | None = None,
    week_gb: str = "0",
    setup_rankings: bool = True,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (
        await movie_import.import_kofic_weekly(
            target_date=target_date,
            week_gb=week_gb,
            setup_rankings=setup_rankings,
        )
    ).to_schema()


@movie_import_router.post("/import/enrich-posters", response_model=MovieImportResultSchema)
async def enrich_missing_posters(
    limit: int = 30,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (await movie_import.enrich_missing_posters(limit=limit)).to_schema()


@movie_import_router.post("/import/kofic/movie/{movie_cd}", response_model=MovieImportResultSchema)
async def import_kofic_movie(
    movie_cd: str,
    movie_import: MovieImportUseCase = Depends(get_movie_import_use_case),
) -> MovieImportResultSchema:
    return (await movie_import.import_by_kofic_cd(movie_cd)).to_schema()
