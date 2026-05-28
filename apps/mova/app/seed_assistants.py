"""Mova AI assistants 시드."""

import logging

from sqlalchemy import select

from core.database import get_session_factory
from mova.app.models.assistants_model import MovaAssistant

logger = logging.getLogger(__name__)

DEFAULT_ASSISTANT = {
    "slug": "mova-concierge",
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
    factory = get_session_factory()
    async with factory() as session:
        result = await session.execute(select(MovaAssistant.id).limit(1))
        if result.scalar_one_or_none() is not None:
            return
        session.add(MovaAssistant(**DEFAULT_ASSISTANT))
        await session.commit()
        logger.info("[mova.seed_assistants] default assistant 생성")
