from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.chat_schema import (
        MovaChatRecommendationSchema,
        MovaChatRequest,
        MovaChatResponseSchema,
    )


@dataclass
class ChatMessageCommand:
    message: str
    history: list[dict[str, str]] = field(default_factory=list)
    model_key: Literal["flash", "flash15", "pro"] | None = None
    user_id: int | None = None

    @classmethod
    def from_request(cls, req: MovaChatRequest) -> ChatMessageCommand:
        return cls(
            message=req.message,
            history=req.history_dicts(),
            model_key=req.model,
            user_id=req.user_id,
        )


@dataclass
class ChatUpsertCommand:
    raw_message: str
    refined_query: str
    keywords: list[str]
    intent_type: str
    search_filters: dict[str, Any]
    user_id: int | None = None
    assistant_id: int | None = None


@dataclass
class ChatResponseDto:
    reply: str
    recommendations: list[MovaChatRecommendationSchema] = field(default_factory=list)
    refined_query: str | None = None
    keywords: list[str] = field(default_factory=list)
    intent_type: str | None = None
    search_filters: dict[str, Any] = field(default_factory=dict)

    def to_schema(self) -> MovaChatResponseSchema:
        from mova.adapter.inbound.api.schemas.chat_schema import MovaChatResponseSchema

        return MovaChatResponseSchema(
            reply=self.reply,
            recommendations=self.recommendations,
            refined_query=self.refined_query,
            keywords=self.keywords,
            intent_type=self.intent_type,
            search_filters=self.search_filters,
        )
