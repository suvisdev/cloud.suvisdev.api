from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.assistants_orm import MovaAssistant
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.app.ports.output.assistants_repository import AssistantsRepository

logger = logging.getLogger(__name__)

DEFAULT_ASSISTANT_SLUG = "mova-concierge"

DEFAULT_ASSISTANT = {
    "slug": DEFAULT_ASSISTANT_SLUG,
    "display_name": "Mova AI 컨시어지",
    "avatar_url": "",
    "system_prompt": (
        "당신은 영화 추천 서비스 Mova의 AI 컨시어지입니다. "
        "사용자 취향·분위기·OTT를 반영해 한국어로 친절하게 답하고, "
        "추천은 반드시 JSON picks 형식을 따릅니다."
    ),
    "default_model": "flash15",
}


async def seed_assistants_if_empty() -> None:
    """assistants 테이블이 비어 있으면 기본 컨시어지 1건을 넣는다 (앱 startup·마이그레이션 스크립트용)."""

    async def work(session: AsyncSession) -> None:
        result = await session.execute(select(MovaAssistant.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return
        session.add(MovaAssistant(**DEFAULT_ASSISTANT))
        logger.info("[AssistantsPgRepository] default assistant 생성 — slug=%s", DEFAULT_ASSISTANT_SLUG)

    await run_pg(None, work)


class AssistantsPgRepository(AssistantsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def get_by_slug(self, slug: str) -> MovaAssistant | None:
        key = slug.strip()[:64]
        if not key:
            return None

        async def work(session: AsyncSession) -> MovaAssistant | None:
            result = await session.execute(
                select(MovaAssistant).where(MovaAssistant.slug == key),
            )
            return result.scalar_one_or_none()

        return await run_pg(self._session, work)

    async def get_default(self) -> MovaAssistant | None:
        row = await self.get_by_slug(DEFAULT_ASSISTANT_SLUG)
        if row is not None and row.is_active:
            return row

        async def work(session: AsyncSession) -> MovaAssistant | None:
            result = await session.execute(
                select(MovaAssistant)
                .where(MovaAssistant.is_active.is_(True))
                .order_by(MovaAssistant.id.asc())
                .limit(1),
            )
            return result.scalar_one_or_none()

        return await run_pg(self._session, work)
