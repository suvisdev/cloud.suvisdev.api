from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.search_pg_repository import SearchPgRepository
from mova.app.ports.input.search_use_case import SearchUseCase
from mova.app.ports.output.search_repository import SearchRepository
from mova.app.use_cases.search_interactor import SearchInteractor


def get_search_use_case(db: AsyncSession = Depends(get_db)) -> SearchUseCase:
    repository: SearchRepository = SearchPgRepository(session=db)
    return SearchInteractor(repository=repository)
