from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from fastapi import Depends

from mova.adapter.outbound.pg.market_chat_pg_repository import MarketChatPgRepository
from mova.app.ports.input.market_chat_use_case import MarketChatUseCase
from mova.app.ports.output.market_chat_repository import MarketChatRepository
from mova.app.use_cases.market_chat_interactor import MarketChatInteractor


def get_market_chat_repository(
    db: AsyncSession = Depends(get_db),
) -> MarketChatRepository:
    return MarketChatPgRepository(session=db)


def get_market_chat_use_case(
    repository: MarketChatRepository = Depends(get_market_chat_repository),
) -> MarketChatUseCase:
    return MarketChatInteractor(repository=repository)
