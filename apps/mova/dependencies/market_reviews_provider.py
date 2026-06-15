from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.market_reviews_pg_repository import MarketReviewsPgRepository
from mova.app.ports.input.market_reviews_use_case import MarketReviewsUseCase
from mova.app.ports.output.market_reviews_repository import MarketReviewsRepository
from mova.app.use_cases.market_reviews_interactor import MarketReviewsInteractor


def get_market_reviews_repository(
    db: AsyncSession = Depends(get_db),
) -> MarketReviewsRepository:
    return MarketReviewsPgRepository(session=db)


def get_market_reviews_use_case(
    repository: MarketReviewsRepository = Depends(get_market_reviews_repository),
) -> MarketReviewsUseCase:
    return MarketReviewsInteractor(repository=repository)
