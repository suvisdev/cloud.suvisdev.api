from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.studio_characters_dto import StudioCharactersQuery, StudioCharactersResponse
from mova.app.ports.output.studio_characters_repository import StudioCharactersRepository

logger = logging.getLogger(__name__)


class StudioCharactersPgRepository(StudioCharactersRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: StudioCharactersQuery) -> StudioCharactersResponse:
        logger.info("[StudioCharactersPgRepository] introduce_myself | query=%s", query)
        return StudioCharactersResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
