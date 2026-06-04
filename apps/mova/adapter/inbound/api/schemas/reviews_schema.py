from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReviewActivityType = Literal["favorite", "watched", "click", "not_interested"]


class ReviewActivityCreateSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)
    action_type: ReviewActivityType = Field(
        ...,
        description="favorite=찜하기, watched=봤어요, click=클릭, not_interested=관심 없음",
    )


class ReviewActivitySchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    action_type: str
    action_at: datetime
    rating: float | None = None
    body: str | None = None


class ReviewActivityWithMovieSchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    action_type: str
    action_at: datetime
    movie_title: str
    movie_slug: str
    rating: float | None = None
    body: str | None = None


class ReviewCreateSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)
    rating: float = Field(..., ge=1, le=5, description="별점 1~5")
    body: str = Field(default="", max_length=4000, description="감상평")


class ReviewUpdateSchema(BaseModel):
    rating: float | None = Field(default=None, ge=1, le=5)
    body: str | None = Field(default=None, max_length=4000)


class ReviewSchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: float
    body: str
    created_at: datetime


class ReviewWithUserSchema(BaseModel):
    id: int
    user_id: int
    nickname: str
    movie_id: int
    rating: float
    body: str
    created_at: datetime


class MovieRatingSummarySchema(BaseModel):
    movie_id: int
    average_rating: float
    review_count: int
