import logging

from mova.app.schemas.actors_schema import ActorCreateSchema, ActorSchema
from mova.app.services.actors_service import ActorsService

logger = logging.getLogger(__name__)


class ActorsController:
    def __init__(self) -> None:
        self.actors_service = ActorsService()

    async def save_actor(self, payload: ActorCreateSchema) -> ActorSchema:
        logger.info("[ActorsController] save_actor — %r", payload.name)
        return await self.actors_service.save_actor(payload)

    async def save_name(self, payload: ActorCreateSchema) -> ActorSchema:
        return await self.actors_service.save_name(payload)

    async def list_actors(self, limit: int = 100) -> list[ActorSchema]:
        return await self.actors_service.list_actors(limit=limit)

    async def list_names(self, limit: int = 100) -> list[ActorSchema]:
        return await self.actors_service.list_names(limit=limit)

    async def get_actor(self, actor_id: int) -> ActorSchema:
        return await self.actors_service.get_actor(actor_id)
