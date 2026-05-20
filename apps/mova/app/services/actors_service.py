import logging

from mova.app.repositories.actors_repository import ActorsRepository, ActorsRepositoryError
from mova.app.schemas.actors_schema import ActorCreateSchema, ActorSchema

logger = logging.getLogger(__name__)


class ActorsService:
    def __init__(self) -> None:
        self.actors_repository = ActorsRepository()

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
        logger.info("[ActorsService] save_actor — %r (%s)", payload.name, payload.role_type)
        row = await self.actors_repository.upsert(self._create_to_dict(payload))
        return self._to_schema(row)

    async def save_name(self, payload: ActorCreateSchema) -> ActorSchema:
        return await self.save_actor(payload)

    async def save_names(self, names: list[str]) -> list[ActorSchema]:
        cleaned = [n.strip() for n in names if n and str(n).strip()]
        if not cleaned:
            return []

        seen: set[str] = set()
        unique: list[str] = []
        for n in cleaned:
            if n not in seen:
                seen.add(n)
                unique.append(n)

        logger.info("[ActorsService] save_names — count=%s", len(unique))
        ids = await self.actors_repository.upsert_names(unique)
        return [
            ActorSchema(id=actor_id, name=name, role_type="actor", profile_photo="")
            for actor_id, name in zip(ids, unique)
        ]

    async def list_actors(self, limit: int = 100) -> list[ActorSchema]:
        rows = await self.actors_repository.list_actors(limit=limit)
        return [self._to_schema(r) for r in rows]

    async def list_names(self, limit: int = 100) -> list[ActorSchema]:
        return await self.list_actors(limit=limit)

    async def get_actor(self, actor_id: int) -> ActorSchema:
        row = await self.actors_repository.get_by_id(actor_id)
        if row is None:
            raise ActorsRepositoryError(
                f"인물 ID {actor_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        return self._to_schema(row)
