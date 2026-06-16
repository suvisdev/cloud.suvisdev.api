"""picks PgRepository — PicksRepositoryPort 구현체."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.market_picks_orm import MovaPick
from mova.app.dtos.market_picks_dto import PickFeedbackDto
from mova.app.ports.output.market_picks_repository import PicksRepositoryPort

logger = logging.getLogger(__name__)

_VALID_FEEDBACK = frozenset({"like", "dislike"})


class PicksPgRepository(PicksRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def update_feedback(self, pick_id: int, feedback: str | None) -> PickFeedbackDto:
        normalized = feedback.strip().lower() if feedback else None
        if normalized and normalized not in _VALID_FEEDBACK:
            normalized = None

        pick = (
            await self._session.execute(
                select(MovaPick).where(MovaPick.id == pick_id)
            )
        ).scalar_one_or_none()

        if pick is None:
            logger.debug("[PicksPgRepository] pick_id=%d 없음", pick_id)
            return PickFeedbackDto(pick_id=pick_id, feedback=None, updated=False)

        pick.feedback = normalized
        await self._session.commit()
        logger.debug("[PicksPgRepository] feedback 업데이트 pick_id=%d → %s", pick_id, normalized)
        return PickFeedbackDto(pick_id=pick_id, feedback=normalized, updated=True)
