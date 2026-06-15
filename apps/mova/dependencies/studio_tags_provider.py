from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.studio_tags_pg_repository import StudioTagsPgRepository
from mova.app.ports.input.studio_tags_use_case import StudioTagsUseCase
from mova.app.ports.output.studio_tags_repository import StudioTagsRepository
from mova.app.use_cases.studio_tags_interactor import StudioTagsInteractor


def get_studio_tags_repository(
    db: AsyncSession = Depends(get_db),
) -> StudioTagsRepository:
    return StudioTagsPgRepository(session=db)


def get_studio_tags_use_case(
    repository: StudioTagsRepository = Depends(get_studio_tags_repository),
) -> StudioTagsUseCase:
    return StudioTagsInteractor(repository=repository)
