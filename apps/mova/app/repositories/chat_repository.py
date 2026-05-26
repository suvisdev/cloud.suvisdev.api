import logging
from datetime import datetime, timezone

from sqlalchemy import func, select

from database import get_session_factory
from mova.app.models.chat_model import MovaChat
from mova.app.services.intent_extraction_service import MAX_CHAT_KEYWORDS, merge_keyword_lists
from secom.app.user_lookup import secom_user_exists

logger = logging.getLogger(__name__)


class ChatRepository:
    async def upsert(
        self,
        raw_message: str,
        refined_query: str,
        keywords: list[str] | None = None,
        *,
        intent_type: str = "mood",
        search_filters: dict | None = None,
        user_id: int | None = None,
        member_id: int | None = None,
        assistant_id: int | None = None,
    ) -> int:
        refined = refined_query.strip()[:255]
        if not refined:
            refined = raw_message.strip()[:255]

        normalized = refined.lower()
        kw_list = merge_keyword_lists(keywords or [], limit=MAX_CHAT_KEYWORDS)
        filters = search_filters if isinstance(search_filters, dict) else {}
        intent = (intent_type or "mood").strip()[:32] or "mood"
        now = datetime.now(timezone.utc)

        if user_id is not None and not await secom_user_exists(user_id):
            raise ValueError(f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)")

        logger.info(
            "[ChatRepository] upsert — user_id=%s member_id=%s assistant_id=%s intent=%s",
            user_id,
            member_id,
            assistant_id,
            intent,
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
                    member_id=member_id,
                    assistant_id=assistant_id,
                    raw_message=raw_message.strip()[:2000],
                    refined_query=refined,
                    keywords=kw_list,
                    intent_type=intent,
                    search_filters=filters,
                    hit_count=1,
                    last_used_at=now,
                )
                session.add(row)
            else:
                row.hit_count += 1
                row.last_used_at = now
                row.raw_message = raw_message.strip()[:2000]
                row.intent_type = intent
                row.search_filters = filters
                if member_id is not None:
                    row.member_id = member_id
                if assistant_id is not None:
                    row.assistant_id = assistant_id
                if kw_list:
                    row.keywords = merge_keyword_lists(row.keywords or [], kw_list, limit=MAX_CHAT_KEYWORDS)

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
