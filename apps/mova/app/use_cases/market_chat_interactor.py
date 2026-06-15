from __future__ import annotations

from mova.adapter.inbound.api.schemas.market_chat_schema import MarketChatSchema
from mova.app.dtos.market_chat_dto import MarketChatQuery, MarketChatResponse
from mova.app.ports.input.market_chat_use_case import MarketChatUseCase
from mova.app.ports.output.market_chat_repository import MarketChatRepository


class MarketChatInteractor(MarketChatUseCase):
    def __init__(self, repository: MarketChatRepository) -> None:
        self._repository = repository

    async def introduce_myself(self, schemas: MarketChatSchema) -> MarketChatResponse:
        return await self._repository.introduce_myself(MarketChatQuery(
            id=schemas.id,
            name=schemas.name,
        ))
