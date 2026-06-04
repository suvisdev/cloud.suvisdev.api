from typing import Literal

from pydantic import BaseModel, Field

MatchType = Literal["title", "person", "keyword", "synopsis"]


class MovaSearchItemSchema(BaseModel):
    """프론트 `MovaSearchResult` 와 동일한 필드."""

    id: str = Field(..., description="영화 slug (`/mova/title/{id}`)")
    title: str
    year: str
    rating: float
    poster: str
    match_type: MatchType


class MovaTitleCastSchema(BaseModel):
    name: str
    role: str
    photo: str = ""


class MovaTitleDetailSchema(BaseModel):
    """프론트 `MovaMovie` 상세 페이지용 (DB 기반 최소 필드)."""

    id: str
    title: str
    year: str
    genres: list[str] = Field(default_factory=list)
    country: str = ""
    ageRating: str = ""
    platform: str | None = None
    poster: str = ""
    backdrop: str = ""
    rating: float = 0.0
    ratingCount: int = 0
    rank: int = 0
    synopsis: str = ""
    ratingDistribution: list[float] = Field(default_factory=lambda: [0.0] * 10)
    cast: list[MovaTitleCastSchema] = Field(default_factory=list)
    comments: list[dict] = Field(default_factory=list)
    gallery: list[str] = Field(default_factory=list)
