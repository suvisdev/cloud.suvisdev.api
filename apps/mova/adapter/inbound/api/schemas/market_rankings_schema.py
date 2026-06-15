from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class RankingItemSchema(BaseModel):
    rank: int
    movie_id: int
    chat_id: int | None = None
    score: int | None = None
    badge: str | None = None


class RankingBulkSchema(BaseModel):
    ranked_at: date | None = None
    source: str = "box_office"
    items: list[RankingItemSchema] = Field(default_factory=list)


class HotRankingDisplaySchema(BaseModel):
    id: int
    rank: int
    movie_id: int
    chat_id: int | None
    source: str
    score: int | None
    badge: str | None
    ranked_at: date
    refined_query: str | None
    slug: str
    title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None
    genres: list[str]


class MarketRankingsSchema(BaseModel):

    id: int = Field(0, description="Rankings ID")
    name: str = Field("프로듀서 (Producer)", description="Producer's name")
    # 흥행 성적을 숫자로 증명하는 제작 총괄. rankings 테이블 관리

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "프로듀서 (Producer)",
            }
        }
    }
