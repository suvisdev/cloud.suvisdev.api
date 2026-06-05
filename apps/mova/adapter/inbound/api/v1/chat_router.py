from __future__ import annotations

from fastapi import APIRouter, Depends

from mova.adapter.inbound.api.http_errors import invoke
from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRequest, MovaChatResponseSchema
from mova.app.ports.input.chat_use_case import ChatUseCase
from mova.dependencies.chat import get_chat_use_case

chat_router = APIRouter(tags=["mova-chat"])


@chat_router.post("/chat", response_model=MovaChatResponseSchema)
async def mova_chat(
    req: MovaChatRequest,
    chat: ChatUseCase = Depends(get_chat_use_case),
) -> MovaChatResponseSchema:
    """Mova AI 영화 추천 채팅."""
    return await invoke(chat.chat_from_request(req), chat=True)
