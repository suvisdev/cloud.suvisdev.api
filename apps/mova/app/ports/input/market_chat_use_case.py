from __future__ import annotations
from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.market_chat_schema import MarketChatSchema
from mova.app.dtos.market_chat_dto import MarketChatResponse


class MarketChatUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schemas: MarketChatSchema) -> MarketChatResponse:
        pass
