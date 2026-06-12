from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.llm.intent_extraction import MAX_CHAT_KEYWORDS, merge_keyword_lists
from mova.adapter.outbound.orm.chat_orm import MovaChat
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.app.dtos.chat_dto import ChatUpsertCommand
from mova.app.ports.output.chat_repository import ChatRepository
from viewer.adapter.outbound.orm.user_orm import viewer_user_exists

logger = logging.getLogger(__name__)


class ChatPgRepository(ChatRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def upsert(self, command: ChatUpsertCommand) -> int:
        raw_message = command.raw_message
        refined_query = command.refined_query
        keywords = command.keywords
        intent_type = command.intent_type
        search_filters = command.search_filters
        user_id = command.user_id
        assistant_id = command.assistant_id

        refined = refined_query.strip()[:255]
        if not refined:
            refined = raw_message.strip()[:255]

        normalized = refined.lower()
        kw_list = merge_keyword_lists(keywords or [], limit=MAX_CHAT_KEYWORDS)
        filters = search_filters if isinstance(search_filters, dict) else {}
        intent = (intent_type or "mood").strip()[:32] or "mood"
        now = datetime.now(timezone.utc)

        if user_id is not None and not await viewer_user_exists(user_id):
            raise ValueError(f"회원 ID {user_id}를 찾을 수 없습니다. (Viewer users)")

        logger.info(
            "[ChatPgRepository] upsert — user_id=%s assistant_id=%s intent=%s",
            user_id,
            assistant_id,
            intent,
        )

        async def work(session: AsyncSession) -> int:
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
                if assistant_id is not None:
                    row.assistant_id = assistant_id
                if kw_list:
                    row.keywords = merge_keyword_lists(
                        row.keywords or [], kw_list, limit=MAX_CHAT_KEYWORDS
                    )

            await session.flush()
            await session.refresh(row)
            return row.id

        return await run_pg(self._session, work)

    async def get_top_for_context(
        self,
        limit: int = 6,
        *,
        user_id: int | None = None,
    ) -> list[MovaChat]:
        async def work(session: AsyncSession) -> list[MovaChat]:
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

        return await run_pg(self._session, work)
