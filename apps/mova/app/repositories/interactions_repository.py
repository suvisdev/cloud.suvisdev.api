import logging
from datetime import datetime, timezone

from sqlalchemy import select

from database import get_session_factory
from mova.app.models.interactions_model import VALID_ACTION_TYPES, MovaInteraction
from mova.app.models.movies_model import MovaMovie
from mova.app.models.users_model import MovaUser

logger = logging.getLogger(__name__)


class InteractionsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InteractionsRepository:
    async def record(
        self,
        *,
        user_id: int,
        movie_id: int,
        action_type: str,
        action_at: datetime | None = None,
    ) -> MovaInteraction:
        normalized = action_type.strip().lower()
        if normalized not in VALID_ACTION_TYPES:
            raise InteractionsRepositoryError(
                "action_type은 favorite, watched, click, not_interested 중 하나여야 합니다.",
                status_code=400,
            )

        logger.info(
            "[InteractionsRepository] record — user=%s movie=%s action=%s",
            user_id,
            movie_id,
            normalized,
        )
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaUser, user_id) is None:
                raise InteractionsRepositoryError(
                    f"사용자 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            if await session.get(MovaMovie, movie_id) is None:
                raise InteractionsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            when = action_at or datetime.now(timezone.utc)
            row = MovaInteraction(
                user_id=user_id,
                movie_id=movie_id,
                action_type=normalized,
                action_at=when,
            )
            session.add(row)
            await session.commit()
            await session.refresh(row)
            return row

    async def list_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[MovaInteraction]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaUser, user_id) is None:
                raise InteractionsRepositoryError(
                    f"사용자 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            stmt = (
                select(MovaInteraction)
                .where(MovaInteraction.user_id == user_id)
                .order_by(MovaInteraction.action_at.desc())
                .limit(limit)
            )
            if action_type:
                stmt = stmt.where(MovaInteraction.action_type == action_type.strip().lower())
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def list_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[tuple[MovaInteraction, MovaMovie]]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaUser, user_id) is None:
                raise InteractionsRepositoryError(
                    f"사용자 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            stmt = (
                select(MovaInteraction, MovaMovie)
                .join(MovaMovie, MovaInteraction.movie_id == MovaMovie.id)
                .where(MovaInteraction.user_id == user_id)
                .order_by(MovaInteraction.action_at.desc())
                .limit(limit)
            )
            if action_type:
                stmt = stmt.where(MovaInteraction.action_type == action_type.strip().lower())
            result = await session.execute(stmt)
            return [(row[0], row[1]) for row in result.all()]
