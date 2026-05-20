import logging

from mova.app.schemas.interactions_schema import (
    InteractionCreateSchema,
    InteractionSchema,
    InteractionWithMovieSchema,
)
from mova.app.services.interactions_service import InteractionsService

logger = logging.getLogger(__name__)


class InteractionsController:
    def __init__(self) -> None:
        self.service = InteractionsService()

    async def record(self, payload: InteractionCreateSchema) -> InteractionSchema:
        logger.info(
            "[InteractionsController] record — user=%s movie=%s",
            payload.user_id,
            payload.movie_id,
        )
        return await self.service.record(payload)

    async def list_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
        with_movies: bool = False,
    ) -> list[InteractionSchema] | list[InteractionWithMovieSchema]:
        if with_movies:
            return await self.service.list_by_user_with_movies(
                user_id,
                action_type=action_type,
                limit=limit,
            )
        return await self.service.list_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )
