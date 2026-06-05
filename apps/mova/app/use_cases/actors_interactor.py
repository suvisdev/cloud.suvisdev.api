from __future__ import annotations

from mova.adapter.inbound.api.schemas.actors_schema import ActorCreateSchema, ActorSchema
from mova.adapter.outbound.pg.actors_pg_repository import ActorsRepositoryError
from mova.app.ports.input.actors_use_case import ActorsUseCase
from mova.app.ports.output.actors_repository import ActorsRepository


class ActorsInteractor(ActorsUseCase):
    def __init__(self, repository: ActorsRepository) -> None:
        self._repository = repository

    def _to_schema(self, row) -> ActorSchema:
        return ActorSchema(
            id=row.id,
            name=row.name,
            role_type=row.role_type,
            profile_photo=row.profile_photo_url,
        )

    def _create_to_dict(self, payload: ActorCreateSchema) -> dict:
        return {
            "name": payload.name,
            "role_type": payload.role_type,
            "profile_photo": payload.profile_photo,
        }

    async def save_actor(self, payload: ActorCreateSchema) -> ActorSchema:
        row = await self._repository.upsert(self._create_to_dict(payload))
        return self._to_schema(row)

    async def save_name(self, payload: ActorCreateSchema) -> ActorSchema:
        return await self.save_actor(payload)

    async def list_actors(self, limit: int = 100) -> list[ActorSchema]:
        rows = await self._repository.list_actors(limit=limit)
        return [self._to_schema(row) for row in rows]

    async def list_names(self, limit: int = 100) -> list[ActorSchema]:
        return await self.list_actors(limit=limit)

    async def get_actor(self, actor_id: int) -> ActorSchema:
        row = await self._repository.get_by_id(actor_id)
        if row is None:
            raise ActorsRepositoryError(
                f"인물 ID {actor_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        return self._to_schema(row)
