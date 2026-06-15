from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.schemas.market_chat_schema import MarketChatSchema
from mova.app.dtos.market_chat_dto import MarketChatResponse
from mova.app.ports.input.market_chat_use_case import MarketChatUseCase
from mova.dependencies.market_chat_provider import get_market_chat_use_case

market_chat_router = APIRouter(prefix="/chat", tags=["mova-chat"])


@market_chat_router.get("/myself")
async def introduce_myself(
    chat: MarketChatUseCase = Depends(get_market_chat_use_case),
) -> MarketChatResponse:
    return await chat.introduce_myself(
        MarketChatSchema(id=1, name="시나리오 작가 (Screenwriter)")
    )
