from fastapi import APIRouter, Depends

from mova.app.dtos.studio_import_dto import StudioImportQuery, StudioImportResponse
from mova.app.ports.input.import_use_case import ImportUseCase
from mova.dependencies.import_provider import get_import_use_case

import_router = APIRouter(prefix="/import", tags=["mova-import"])


@import_router.get("/myself")
async def introduce_myself(
    movie_import: ImportUseCase = Depends(get_import_use_case),
) -> StudioImportResponse:
    return await movie_import.introduce_myself(
        StudioImportQuery(id=1, name="수입 감독 (Import Director)")
    )
