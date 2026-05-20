import logging
from datetime import datetime, timezone

from sqlalchemy import func, select

from database import get_session_factory
from mova.app.models.audience_model import MovaChatIntent

logger = logging.getLogger(__name__)


class ChatIntentRepository:
    async def upsert(
        self,
        raw_message: str,
        refined_query: str,
        keywords: list[str] | None = None,
    ) -> int:
        refined = refined_query.strip()[:255]
        if not refined:
            refined = raw_message.strip()[:255]

        normalized = refined.lower()
        kw_list = [k.strip() for k in (keywords or []) if k and k.strip()][:12]
        now = datetime.now(timezone.utc)

        logger.info(
            "[ChatIntentRepository] upsert — refined=%r keywords=%s",
            refined,
            kw_list,
        )

        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaChatIntent).where(
                    func.lower(MovaChatIntent.refined_query) == normalized,
                ),
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaChatIntent(
                    raw_message=raw_message.strip()[:2000],
                    refined_query=refined,
                    keywords=kw_list,
                    hit_count=1,
                    last_used_at=now,
                )
                session.add(row)
            else:
                row.hit_count += 1
                row.last_used_at = now
                row.raw_message = raw_message.strip()[:2000]
                if kw_list:
                    merged = list(dict.fromkeys([*(row.keywords or []), *kw_list]))
                    row.keywords = merged[:12]

            await session.commit()
            await session.refresh(row)
            return row.id

    async def get_top_for_context(self, limit: int = 6) -> list[MovaChatIntent]:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaChatIntent)
                .order_by(MovaChatIntent.hit_count.desc(), MovaChatIntent.last_used_at.desc())
                .limit(limit),
            )
            return list(result.scalars().all())
