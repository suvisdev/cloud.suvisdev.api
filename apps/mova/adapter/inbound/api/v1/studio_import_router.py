from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.studio_import_schema import StudioImportSchema
from mova.app.dtos.studio_import_dto import StudioImportResponse
from mova.app.ports.input.studio_import_use_case import StudioImportUseCase
from mova.dependencies.studio_import_provider import get_studio_import_use_case

studio_import_router = APIRouter(prefix="/import", tags=["mova-import"])


@studio_import_router.get("/myself")
async def introduce_myself(
    movie_import: StudioImportUseCase = Depends(get_studio_import_use_case),
) -> StudioImportResponse:
    return await movie_import.introduce_myself(
        StudioImportSchema(id=1, name="수입 감독 (Import Director)")
    )
