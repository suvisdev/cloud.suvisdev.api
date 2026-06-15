from __future__ import annotations

from abc import ABC, abstractmethod

from mova.app.dtos.market_chat_dto import MarketChatQuery, MarketChatResponse


class MarketChatRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: MarketChatQuery) -> MarketChatResponse:
        pass
