from __future__ import annotations

from abc import ABC, abstractmethod

from dispatch.app.dtos.inbox_dto import InboxItem, InboxSaveCommand


class InboxUseCase(ABC):
    @abstractmethod
    async def save(self, command: InboxSaveCommand) -> InboxItem: ...

    @abstractmethod
    async def list_all(self, limit: int) -> list[InboxItem]: ...

    @abstractmethod
    async def delete(self, item_id: int) -> None: ...
