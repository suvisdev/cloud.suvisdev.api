from fastapi import APIRouter, Depends, HTTPException

from mova.adapter.inbound.api.schemas.studio_import_schema import (
    MovieImportResultSchema,
    TmdbImportRequestSchema,
)
from mova.adapter.outbound.http.tmdb_adapter import TmdbAdapterError
from mova.app.dtos.studio_import_dto import StudioImportQuery, TmdbImportCommand
from mova.app.ports.input.import_use_case import ImportUseCase
from mova.dependencies.import_provider import get_import_use_case

import_router = APIRouter(prefix="/import", tags=["mova-import"])


@import_router.get("/myself")
async def introduce_myself(
    movie_import: ImportUseCase = Depends(get_import_use_case),
) -> dict[str, int | str]:
    dto = await movie_import.introduce_myself(
        StudioImportQuery(id=1, name="수입 감독 (Import Director)")
    )
    return {"id": dto.id, "name": dto.name}


@import_router.post("/tmdb", response_model=MovieImportResultSchema)
async def import_from_tmdb(
    req: TmdbImportRequestSchema,
    use_case: ImportUseCase = Depends(get_import_use_case),
) -> MovieImportResultSchema:
    """TMDB에서 영화 메타를 가져와 카탈로그에 반영."""
    if req.tmdb_id is None and not (req.query and req.query.strip()) and req.popular_pages <= 0:
        raise HTTPException(
            status_code=400,
            detail="tmdb_id, query, popular_pages 중 하나는 필요합니다.",
        )
    command = TmdbImportCommand(
        tmdb_id=req.tmdb_id,
        query=req.query.strip() if req.query else None,
        popular_pages=req.popular_pages,
    )
    try:
        dto = await use_case.import_tmdb(command)
    except TmdbAdapterError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e)) from e
    return dto.to_schema()
