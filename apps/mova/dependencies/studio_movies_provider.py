from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.studio_movies_pg_repository import StudioMoviesPgRepository
from mova.app.ports.input.studio_movies_use_case import StudioMoviesUseCase
from mova.app.ports.output.studio_movies_repository import StudioMoviesRepository
from mova.app.use_cases.studio_movies_interactor import StudioMoviesInteractor


def get_studio_movies_repository(
    db: AsyncSession = Depends(get_db),
) -> StudioMoviesRepository:
    return StudioMoviesPgRepository(session=db)


def get_studio_movies_use_case(
    repository: StudioMoviesRepository = Depends(get_studio_movies_repository),
) -> StudioMoviesUseCase:
    return StudioMoviesInteractor(repository=repository)
