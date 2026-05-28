import logging

from sqlalchemy import select

from core.database import get_session_factory
from mova.app.models.assistants_model import MovaAssistant

logger = logging.getLogger(__name__)

DEFAULT_ASSISTANT_SLUG = "mova-concierge"


class AssistantsRepository:
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
