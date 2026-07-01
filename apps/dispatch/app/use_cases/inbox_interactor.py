from __future__ import annotations

from dispatch.app.dtos.inbox_dto import InboxItem, InboxSaveCommand
from dispatch.app.ports.input.inbox_use_case import InboxUseCase
from dispatch.app.ports.output.inbox_port import InboxPort


class InboxInteractor(InboxUseCase):
    def __init__(self, *, repository: InboxPort) -> None:
        self._repository = repository

    async def save(self, command: InboxSaveCommand) -> InboxItem:
        return await self._repository.save(command)

    async def list_all(self, limit: int) -> list[InboxItem]:
        return await self._repository.list_all(limit)

    async def delete(self, item_id: int) -> None:
        await self._repository.delete(item_id)
