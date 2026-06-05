from datetime import date

from pydantic import BaseModel, Field

from mova.domain.value_objects.ranking_source import (
    DEFAULT_HOT_RANKING_SOURCE,
    RANKING_SOURCE_BOX_OFFICE,
)


class RankingItemCreateSchema(BaseModel):
    rank: int = Field(..., ge=1, le=100, description="랭킹 순위 (1=1위)")
    movie_id: int = Field(..., gt=0, description="영화 ID (`movies.id`)")
    chat_id: int | None = Field(default=None, description="대표 chat.id (chat_trend)")
    score: int | None = Field(default=None, description="집계 점수")
    badge: str | None = Field(default=None, description="변동 표시: NEW | HOT | AD")
    ranked_at: date | None = Field(default=None, description="랭킹 산정 기준일 (미입력=오늘)")


class RankingBulkSchema(BaseModel):
    ranked_at: date | None = Field(default=None, description="일괄 저장 기준일 (미입력=오늘)")
    source: str = Field(default=RANKING_SOURCE_BOX_OFFICE, description="chat_trend | box_office | manual")
    items: list[RankingItemCreateSchema] = Field(..., min_length=1, max_length=50)


class RankingItemSchema(BaseModel):
    id: int
    rank: int
    movie_id: int
    chat_id: int | None = None
    source: str
    score: int | None = None
    badge: str | None = None
    ranked_at: date


class HotRankingDisplaySchema(BaseModel):
    """HOT 랭킹 UI용 — 랭킹 + 영화 + (chat_trend 시) 검색어."""

    id: int
    rank: int
    movie_id: int
    chat_id: int | None = None
    source: str = DEFAULT_HOT_RANKING_SOURCE
    score: int | None = None
    badge: str | None = None
    ranked_at: date
    refined_query: str | None = None
    slug: str
    title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None = None
    genres: list[str] = Field(default_factory=list)
