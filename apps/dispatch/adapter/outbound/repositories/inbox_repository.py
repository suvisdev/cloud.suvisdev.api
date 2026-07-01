from __future__ import annotations

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from dispatch.adapter.outbound.orm.inbox_orm import DispatchInboxOrm
from dispatch.app.dtos.inbox_dto import InboxItem, InboxSaveCommand
from dispatch.app.ports.output.inbox_port import InboxPort


class InboxRepository(InboxPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, command: InboxSaveCommand) -> InboxItem:
        row = DispatchInboxOrm(
            sender=command.sender,
            subject=command.subject,
            body=command.body,
            received_at=datetime.utcnow(),
        )
        self._session.add(row)
        await self._session.flush()
        return _to_item(row)

    async def list_all(self, limit: int) -> list[InboxItem]:
        stmt = select(DispatchInboxOrm).order_by(DispatchInboxOrm.received_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return [_to_item(row) for row in result.scalars().all()]

    async def delete(self, item_id: int) -> None:
        await self._session.execute(delete(DispatchInboxOrm).where(DispatchInboxOrm.id == item_id))


def _to_item(row: DispatchInboxOrm) -> InboxItem:
    return InboxItem(
        id=row.id,
        sender=row.sender,
        subject=row.subject,
        body=row.body,
        received_at=row.received_at,
    )
