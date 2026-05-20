from typing import Literal

from pydantic import BaseModel, Field


class MovieCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(default=None, max_length=64, description="미입력 시 제목에서 생성")
    release_year: str = Field(default="", max_length=8, description="개봉 연도")
    rating: float = Field(default=0.0, ge=0, le=10)
    poster: str = Field(default="", description="포스터 이미지 URL/경로")
    platform: Literal["netflix", "disney"] | None = Field(default=None)
    genres: list[str] = Field(default_factory=list, description="장르 목록")


class MovieSchema(BaseModel):
    id: int
    slug: str
    title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None = None
    genres: list[str] = Field(default_factory=list)


class MovieTitleCreateSchema(BaseModel):
    """채팅 추천 등 제목만 저장할 때 (하위 호환)."""

    title: str = Field(..., min_length=1, max_length=255)


class MovieTitleSchema(BaseModel):
    id: int
    title: str
