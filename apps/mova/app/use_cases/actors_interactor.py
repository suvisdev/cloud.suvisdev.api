from __future__ import annotations

from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema
from mova.adapter.outbound.pg.actors_pg_repository import ActorsRepositoryError
from mova.app.dtos.actors_dto import ActorDto, ActorUpsertCommand
from mova.app.ports.input.actors_use_case import ActorsUseCase
from mova.app.ports.output.actors_repository import ActorsRepository


class ActorsInteractor(ActorsUseCase):
    def __init__(self, repository: ActorsRepository) -> None:
        self._repository = repository

    async def save_actor(self, payload: ActorCreateSchema) -> ActorDto:
        command = ActorUpsertCommand.from_schema(payload)
        row = await self._repository.upsert(command)
        return ActorDto.from_orm(row)

    async def save_name(self, payload: ActorCreateSchema) -> ActorDto:
        return await self.save_actor(payload)

    async def list_actors(self, limit: int = 100) -> list[ActorDto]:
        rows = await self._repository.list_actors(limit=limit)
        return [ActorDto.from_orm(row) for row in rows]

    async def list_names(self, limit: int = 100) -> list[ActorDto]:
        return await self.list_actors(limit=limit)

    async def get_actor(self, actor_id: int) -> ActorDto:
        row = await self._repository.get_by_id(actor_id)
        if row is None:
            raise ActorsRepositoryError(
                f"인물 ID {actor_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        return ActorDto.from_orm(row)
