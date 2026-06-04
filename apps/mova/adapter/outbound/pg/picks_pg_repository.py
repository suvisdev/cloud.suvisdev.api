import logging
from datetime import datetime, timezone

from core.matrix.oracle_database import get_session_factory
from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRecommendationSchema
from mova.adapter.outbound.orm.picks_orm import MovaPick
from mova.app.ports.output.picks_repository import PicksRepository

logger = logging.getLogger(__name__)


class PicksPgRepository(PicksRepository):
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
        factory = get_session_factory()
        async with factory() as session:
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
            await session.commit()
        logger.info(
            "[PicksPgRepository] save_chat_recommendations — chat_id=%s count=%s",
            chat_id,
            len(movie_ids),
        )
        return len(movie_ids)
