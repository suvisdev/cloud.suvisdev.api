from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.movie_import_schema import MovieImportResultSchema
from mova.adapter.outbound.http import KoficAdapter, KoficAdapterError, TmdbAdapterError
from mova.app.ports.input.movie_import_use_case import MovieImportUseCase
from mova.app.use_cases.movie_import_interactor import MovieImportInteractor

movie_import_router = APIRouter(tags=["mova-import"])

logger = logging.getLogger(__name__)


def _validate_kofic_target_date(raw: str) -> str:
    value = raw.strip()
    if len(value) != 8 or not value.isdigit():
        raise HTTPException(status_code=400, detail="target_date 형식은 YYYYMMDD 입니다.")
    return value


@movie_import_router.post("/import/tmdb/popular", response_model=MovieImportResultSchema)
async def import_tmdb_popular(
    pages: int = 2,
    setup_rankings: bool = True,
) -> MovieImportResultSchema:
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.import_popular(
            pages=min(max(pages, 1), 5),
            setup_rankings=setup_rankings,
        )
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movie_import_router.post("/import/tmdb/search", response_model=MovieImportResultSchema)
async def import_tmdb_search(
    q: str,
    pages: int = 1,
    setup_rankings: bool = False,
) -> MovieImportResultSchema:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="검색어 q가 비어 있습니다.")
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.import_search(
            query,
            pages=min(max(pages, 1), 3),
            setup_rankings=setup_rankings,
        )
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movie_import_router.post("/import/tmdb/movie/{tmdb_id}", response_model=MovieImportResultSchema)
async def import_tmdb_movie(tmdb_id: int) -> MovieImportResultSchema:
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.import_by_tmdb_id(tmdb_id)
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movie_import_router.post("/import/kofic/daily", response_model=MovieImportResultSchema)
async def import_kofic_daily(
    target_date: str | None = None,
    setup_rankings: bool = True,
) -> MovieImportResultSchema:
    date_arg = _validate_kofic_target_date(target_date or KoficAdapter.default_target_date())
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.import_kofic_daily(
            target_date=date_arg,
            setup_rankings=setup_rankings,
        )
    except KoficAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movie_import_router.post("/import/kofic/weekly", response_model=MovieImportResultSchema)
async def import_kofic_weekly(
    target_date: str | None = None,
    week_gb: str = "0",
    setup_rankings: bool = True,
) -> MovieImportResultSchema:
    date_arg = _validate_kofic_target_date(target_date or KoficAdapter.default_target_date())
    if week_gb not in ("0", "1"):
        raise HTTPException(status_code=400, detail="week_gb는 0(주간) 또는 1(주말)만 가능합니다.")
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.import_kofic_weekly(
            target_date=date_arg,
            week_gb=week_gb,
            setup_rankings=setup_rankings,
        )
    except KoficAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movie_import_router.post("/import/enrich-posters", response_model=MovieImportResultSchema)
async def enrich_missing_posters(limit: int = 30) -> MovieImportResultSchema:
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.enrich_missing_posters(limit=min(max(limit, 1), 100))
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@movie_import_router.post("/import/kofic/movie/{movie_cd}", response_model=MovieImportResultSchema)
async def import_kofic_movie(movie_cd: str) -> MovieImportResultSchema:
    code = movie_cd.strip()
    if not code:
        raise HTTPException(status_code=400, detail="movie_cd가 비어 있습니다.")
    use_case: MovieImportUseCase = MovieImportInteractor()
    try:
        return await use_case.import_by_kofic_cd(code)
    except KoficAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
