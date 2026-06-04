from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema, ActorSchema


class ActorsUseCase(ABC):
    """인물(actors) 입력 포트."""

    @abstractmethod
    async def save_actor(self, payload: ActorCreateSchema) -> ActorSchema:
        pass

    @abstractmethod
    async def save_name(self, payload: ActorCreateSchema) -> ActorSchema:
        pass

    @abstractmethod
    async def list_actors(self, limit: int = 100) -> list[ActorSchema]:
        pass

    @abstractmethod
    async def list_names(self, limit: int = 100) -> list[ActorSchema]:
        pass

    @abstractmethod
    async def get_actor(self, actor_id: int) -> ActorSchema:
        pass
