from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.outbound.orm.actors_orm import MovaActor
from mova.app.dtos.actors_dto import ActorUpsertCommand


class ActorsRepository(ABC):
    """인물(actors) 아웃바운드 포트."""

    @abstractmethod
    async def get_by_id(self, actor_id: int) -> MovaActor | None:
        pass

    @abstractmethod
    async def upsert(self, command: ActorUpsertCommand) -> MovaActor:
        pass

    @abstractmethod
    async def upsert_name(self, command: ActorUpsertCommand) -> int:
        pass

    @abstractmethod
    async def upsert_names(self, commands: list[ActorUpsertCommand]) -> list[int]:
        pass

    @abstractmethod
    async def list_actors(self, limit: int = 100) -> list[MovaActor]:
        pass

    @abstractmethod
    async def list_names(self, limit: int = 100) -> list[MovaActor]:
        pass
