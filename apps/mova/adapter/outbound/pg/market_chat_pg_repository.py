from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from mova.app.dtos.market_chat_dto import MarketChatQuery, MarketChatResponse
from mova.app.ports.output.market_chat_repository import MarketChatRepository

logger = logging.getLogger(__name__)


class MarketChatPgRepository(MarketChatRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def introduce_myself(self, query: MarketChatQuery) -> MarketChatResponse:
        logger.info("[MarketChatPgRepository] introduce_myself | query=%s", query)
        return MarketChatResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")
