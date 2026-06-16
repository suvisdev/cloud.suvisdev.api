"""채팅 DI."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_mova_db
from mova.adapter.outbound.pg.market_chat_pg_repository import ChatPgRepository
from mova.app.ports.input.market_chat_use_case import ChatUseCase
from mova.app.ports.output.market_chat_repository import ChatRepositoryPort
from mova.app.use_cases.market_chat_interactor import ChatInteractor


def get_chat_repository(
    db: AsyncSession = Depends(get_mova_db),
) -> ChatRepositoryPort:
    return ChatPgRepository(session=db)


def get_chat_use_case(
    repository: ChatRepositoryPort = Depends(get_chat_repository),
) -> ChatUseCase:
    return ChatInteractor(repository=repository)


get_market_chat_use_case = get_chat_use_case
