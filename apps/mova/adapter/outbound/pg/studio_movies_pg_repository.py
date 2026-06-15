from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.studio_movies_dto import StudioMoviesQuery, StudioMoviesResponse
from mova.app.ports.output.studio_movies_repository import StudioMoviesRepository

logger = logging.getLogger(__name__)


class StudioMoviesPgRepository(StudioMoviesRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: StudioMoviesQuery) -> StudioMoviesResponse:
        logger.info("[StudioMoviesPgRepository] introduce_myself | query=%s", query)
        return StudioMoviesResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
