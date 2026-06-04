from datetime import date

from pydantic import BaseModel, Field


class RankingItemCreateSchema(BaseModel):
    rank: int = Field(..., ge=1, le=100, description="랭킹 순위 (1=1위)")
    movie_id: int = Field(..., gt=0, description="영화 ID (`movies.id`)")
    badge: str | None = Field(default=None, description="변동 표시: NEW | AD")
    ranked_at: date | None = Field(default=None, description="랭킹 산정 기준일 (미입력=오늘)")


class RankingBulkSchema(BaseModel):
    ranked_at: date | None = Field(default=None, description="일괄 저장 기준일 (미입력=오늘)")
    items: list[RankingItemCreateSchema] = Field(..., min_length=1, max_length=50)


class RankingItemSchema(BaseModel):
    id: int
    rank: int
    movie_id: int
    badge: str | None = None
    ranked_at: date


class HotRankingDisplaySchema(BaseModel):
    """HOT 랭킹 UI용 — 랭킹 + 영화 정보 조인."""

    id: int
    rank: int
    movie_id: int
    badge: str | None = None
    ranked_at: date
    slug: str
    title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None = None
    genres: list[str] = Field(default_factory=list)
