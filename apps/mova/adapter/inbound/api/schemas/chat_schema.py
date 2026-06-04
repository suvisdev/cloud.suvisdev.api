from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MovaChatRecommendationSchema(BaseModel):
    id: str
    title: str
    year: str
    poster: str
    synopsis: str
    platform: str | None = None
    hook: str = Field(description="한 줄 추천 이유")


class MovaChatResponseSchema(BaseModel):
    reply: str
    recommendations: list[MovaChatRecommendationSchema] = Field(default_factory=list)
    refined_query: str | None = None
    keywords: list[str] = Field(default_factory=list)
    intent_type: str | None = None
    search_filters: dict = Field(default_factory=dict)


class MovaChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class MovaChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[MovaChatHistoryItem] = Field(default_factory=list)
    model: Literal["flash", "flash15", "pro"] | None = None
    user_id: int | None = Field(
        default=None,
        description="Mova 회원 ID — 로그인 사용자 취향·의도 저장에 사용",
    )
