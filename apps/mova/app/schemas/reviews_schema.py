from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreateSchema(BaseModel):
    user_id: int = Field(..., gt=0)
    movie_id: int = Field(..., gt=0)
    rating: float = Field(..., ge=1, le=5, description="별점 1~5 (0.5 단위 가능)")
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
