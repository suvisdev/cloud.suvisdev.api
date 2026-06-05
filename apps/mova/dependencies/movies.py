from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.oracle_database import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.movies_pg_repository import MoviesPgRepository
from mova.app.ports.input.characters_use_case import CharactersUseCase
from mova.app.ports.input.movies_use_case import MoviesUseCase
from mova.app.ports.input.reviews_use_case import ReviewsUseCase
from mova.app.ports.output.movies_repository import MoviesRepository
from mova.app.use_cases.movies_interactor import MoviesInteractor
from mova.dependencies.characters import get_characters_use_case
from mova.dependencies.reviews import get_reviews_use_case


def get_movies_use_case(
    db: AsyncSession = Depends(get_db),
    characters: CharactersUseCase = Depends(get_characters_use_case),
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> MoviesUseCase:
    repository: MoviesRepository = MoviesPgRepository(session=db)
    return MoviesInteractor(
        repository=repository,
        characters_use_case=characters,
        reviews_use_case=reviews,
    )
