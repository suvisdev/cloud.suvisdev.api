"""영화 import DI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_mova_db
from mova.adapter.outbound.pg.movies_pg_repository import MoviesPgRepository
from mova.app.ports.input.import_use_case import ImportUseCase
from mova.app.ports.output.movies_repository import MoviesRepositoryPort
from mova.app.use_cases.import_interactor import ImportInteractor


def get_import_use_case(
    db: AsyncSession = Depends(get_mova_db),
) -> ImportUseCase:
    repository: MoviesRepositoryPort = MoviesPgRepository(session=db)
    return ImportInteractor(repository=repository)
