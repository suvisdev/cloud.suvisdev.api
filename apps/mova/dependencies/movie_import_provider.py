from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.movies_pg_repository import MoviesPgRepository
from mova.app.ports.input.movie_import_use_case import MovieImportUseCase
from mova.app.ports.input.rankings_use_case import RankingsUseCase
from mova.app.ports.output.movies_repository import MoviesRepository
from mova.app.use_cases.movie_import_interactor import MovieImportInteractor
from mova.dependencies.rankings_provider import get_rankings_use_case


def get_movie_import_use_case(
    db: AsyncSession = Depends(get_db),
    rankings: RankingsUseCase = Depends(get_rankings_use_case),
) -> MovieImportUseCase:
    repository: MoviesRepository = MoviesPgRepository(session=db)
    return MovieImportInteractor(
        movies_repository=repository,
        rankings_use_case=rankings,
    )
