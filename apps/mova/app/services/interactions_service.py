import logging

from mova.app.repositories.interactions_repository import InteractionsRepository
from mova.app.schemas.interactions_schema import (
    InteractionCreateSchema,
    InteractionSchema,
    InteractionWithMovieSchema,
)

logger = logging.getLogger(__name__)


class InteractionsService:
    def __init__(self) -> None:
        self.repository = InteractionsRepository()

    def _to_schema(self, row) -> InteractionSchema:
        return InteractionSchema(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            action_type=row.action_type,
            action_at=row.action_at,
        )

    async def record(self, payload: InteractionCreateSchema) -> InteractionSchema:
        logger.info(
            "[InteractionsService] record — user=%s movie=%s %s",
            payload.user_id,
            payload.movie_id,
            payload.action_type,
        )
        row = await self.repository.record(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            action_type=payload.action_type,
        )
        return self._to_schema(row)

    async def list_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[InteractionSchema]:
        rows = await self.repository.list_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )
        return [self._to_schema(r) for r in rows]

    async def list_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[InteractionWithMovieSchema]:
        rows = await self.repository.list_by_user_with_movies(
            user_id,
            action_type=action_type,
            limit=limit,
        )
        return [
            InteractionWithMovieSchema(
                id=interaction.id,
                user_id=interaction.user_id,
                movie_id=interaction.movie_id,
                action_type=interaction.action_type,
                action_at=interaction.action_at,
                movie_title=movie.title,
                movie_slug=movie.slug,
            )
            for interaction, movie in rows
        ]
