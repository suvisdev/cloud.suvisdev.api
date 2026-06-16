"""영화 import DI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_mova_db
from mova.adapter.outbound.pg.studio_movies_pg_repository import MoviesPgRepository
from mova.app.ports.input.studio_import_use_case import StudioImportUseCase
from mova.app.ports.output.studio_movies_repository import MoviesRepositoryPort
from mova.app.use_cases.studio_import_interactor import StudioImportInteractor


def get_studio_import_use_case(
    db: AsyncSession = Depends(get_mova_db),
) -> StudioImportUseCase:
    repository: MoviesRepositoryPort = MoviesPgRepository(session=db)
    return StudioImportInteractor(repository=repository)
