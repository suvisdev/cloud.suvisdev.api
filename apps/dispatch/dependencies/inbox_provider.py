from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.grid_oracle_database_manager import get_db
from dispatch.adapter.outbound.repositories.inbox_repository import InboxRepository
from dispatch.app.ports.input.inbox_use_case import InboxUseCase
from dispatch.app.ports.output.inbox_port import InboxPort
from dispatch.app.use_cases.inbox_interactor import InboxInteractor


def get_inbox_repository(session: AsyncSession = Depends(get_db)) -> InboxPort:
    return InboxRepository(session=session)


def get_inbox_use_case(
    repository: InboxPort = Depends(get_inbox_repository),
) -> InboxUseCase:
    return InboxInteractor(repository=repository)
