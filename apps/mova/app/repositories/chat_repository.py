import logging
from datetime import datetime, timezone

from sqlalchemy import func, select

from database import get_session_factory
from mova.app.models.chat_model import MovaChat
from secom.app.user_lookup import secom_user_exists

logger = logging.getLogger(__name__)


class ChatRepository:
    async def upsert(
        self,
        raw_message: str,
        refined_query: str,
        keywords: list[str] | None = None,
        *,
        user_id: int | None = None,
    ) -> int:
        refined = refined_query.strip()[:255]
        if not refined:
            refined = raw_message.strip()[:255]

        normalized = refined.lower()
        kw_list = [k.strip() for k in (keywords or []) if k and k.strip()][:12]
        now = datetime.now(timezone.utc)

        if user_id is not None and not await secom_user_exists(user_id):
            raise ValueError(f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)")

        logger.info(
            "[ChatRepository] upsert — user_id=%s refined=%r keywords=%s",
            user_id,
            refined,
            kw_list,
        )

        factory = get_session_factory()
        async with factory() as session:
            stmt = select(MovaChat).where(
                func.lower(MovaChat.refined_query) == normalized,
            )
            if user_id is not None:
                stmt = stmt.where(MovaChat.user_id == user_id)
            else:
                stmt = stmt.where(MovaChat.user_id.is_(None))

            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaChat(
                    user_id=user_id,
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

    async def get_top_for_context(
        self,
        limit: int = 6,
        *,
        user_id: int | None = None,
    ) -> list[MovaChat]:
        factory = get_session_factory()
        async with factory() as session:
            stmt = (
                select(MovaChat)
                .order_by(MovaChat.hit_count.desc(), MovaChat.last_used_at.desc())
                .limit(limit)
            )
            if user_id is not None:
                stmt = stmt.where(MovaChat.user_id == user_id)
            else:
                stmt = stmt.where(MovaChat.user_id.is_(None))

            result = await session.execute(stmt)
            return list(result.scalars().all())
