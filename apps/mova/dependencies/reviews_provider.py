from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.reviews_pg_repository import ReviewsPgRepository
from mova.app.ports.input.reviews_use_case import ReviewsUseCase
from mova.app.ports.output.reviews_repository import ReviewsRepository
from mova.app.use_cases.reviews_interactor import ReviewsInteractor


def get_reviews_use_case(db: AsyncSession = Depends(get_db)) -> ReviewsUseCase:
    repository: ReviewsRepository = ReviewsPgRepository(session=db)
    return ReviewsInteractor(repository=repository)
