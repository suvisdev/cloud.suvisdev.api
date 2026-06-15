from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.studio_actors_dto import StudioActorsQuery, StudioActorsResponse
from mova.app.ports.output.studio_actors_repository import StudioActorsRepository

logger = logging.getLogger(__name__)


class StudioActorsPgRepository(StudioActorsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: StudioActorsQuery) -> StudioActorsResponse:
        logger.info("[StudioActorsPgRepository] introduce_myself | query=%s", query)
        return StudioActorsResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
