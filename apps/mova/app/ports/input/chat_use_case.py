from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRequest
from mova.app.dtos.chat_dto import ChatResponseDto


class ChatUseCase(ABC):
    @abstractmethod
    async def prepare_chat_context(
        self,
        message: str,
        *,
        user_id: int | None = None,
    ) -> dict:
        pass

    @abstractmethod
    async def build_prompt(
        self,
        history: list[dict[str, str]],
        message: str,
        context: dict | None = None,
    ) -> str:
        pass

    @abstractmethod
    async def build_response(
        self,
        raw_gemini: str,
        context: dict,
    ) -> ChatResponseDto:
        pass

    @abstractmethod
    async def chat(
        self,
        message: str,
        history: list[dict[str, str]],
        *,
        user_id: int | None = None,
        model_key: Literal["flash", "flash15", "pro"] | None = None,
    ) -> ChatResponseDto:
        pass

    @abstractmethod
    async def chat_from_request(self, req: MovaChatRequest) -> ChatResponseDto:
        pass
