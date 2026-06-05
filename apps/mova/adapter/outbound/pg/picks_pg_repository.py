from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRecommendationSchema
from mova.adapter.outbound.orm.picks_orm import MovaPick
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.app.ports.output.picks_repository import PicksRepository

logger = logging.getLogger(__name__)


class PicksPgRepository(PicksRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def save_chat_recommendations(
        self,
        *,
        chat_id: int,
        user_id: int | None,
        movie_ids: list[tuple[int, MovaChatRecommendationSchema, int]],
    ) -> int:
        if not movie_ids:
            return 0

        batch_at = datetime.now(timezone.utc)

        async def work(session: AsyncSession) -> int:
            for movie_id, rec, rank in movie_ids:
                session.add(
                    MovaPick(
                        chat_id=chat_id,
                        user_id=user_id,
                        movie_id=movie_id,
                        pick_rank=rank,
                        hook=(rec.hook or "")[:120] or None,
                        title_snapshot=rec.title.strip()[:255],
                        batch_at=batch_at,
                    ),
                )
            await session.flush()
            return len(movie_ids)

        count = await run_pg(self._session, work)
        logger.info(
            "[PicksPgRepository] save_chat_recommendations — chat_id=%s count=%s",
            chat_id,
            count,
        )
        return count
