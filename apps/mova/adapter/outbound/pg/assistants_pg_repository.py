import logging

from sqlalchemy import select

from core.matrix.oracle_database import get_session_factory
from mova.adapter.outbound.orm.assistants_orm import MovaAssistant
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
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(MovaAssistant.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return
        session.add(MovaAssistant(**DEFAULT_ASSISTANT))
        await session.commit()
        logger.info("[AssistantsPgRepository] default assistant 생성 — slug=%s", DEFAULT_ASSISTANT_SLUG)


class AssistantsPgRepository(AssistantsRepository):
    async def get_by_slug(self, slug: str) -> MovaAssistant | None:
        key = slug.strip()[:64]
        if not key:
            return None
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaAssistant).where(MovaAssistant.slug == key),
            )
            return result.scalar_one_or_none()

    async def get_default(self) -> MovaAssistant | None:
        row = await self.get_by_slug(DEFAULT_ASSISTANT_SLUG)
        if row is not None and row.is_active:
            return row
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaAssistant)
                .where(MovaAssistant.is_active.is_(True))
                .order_by(MovaAssistant.id.asc())
                .limit(1),
            )
            return result.scalar_one_or_none()
