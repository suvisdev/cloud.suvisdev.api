from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.studio_search_pg_repository import StudioSearchPgRepository
from mova.app.ports.input.studio_search_use_case import StudioSearchUseCase
from mova.app.ports.output.studio_search_repository import StudioSearchRepository
from mova.app.use_cases.studio_search_interactor import StudioSearchInteractor


def get_studio_search_repository(
    db: AsyncSession = Depends(get_db),
) -> StudioSearchRepository:
    return StudioSearchPgRepository(session=db)


def get_studio_search_use_case(
    repository: StudioSearchRepository = Depends(get_studio_search_repository),
) -> StudioSearchUseCase:
    return StudioSearchInteractor(repository=repository)
