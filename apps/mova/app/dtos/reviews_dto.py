from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.reviews_schema import (
        MovieRatingSummarySchema,
        ReviewActivityCreateSchema,
        ReviewActivitySchema,
        ReviewActivityWithMovieSchema,
        ReviewCreateSchema,
        ReviewSchema,
        ReviewUpdateSchema,
        ReviewWithUserSchema,
    )
    from mova.adapter.outbound.orm.movies_orm import MovaMovie
    from mova.adapter.outbound.orm.reviews_orm import MovaReview

ReviewActivityType = Literal["favorite", "watched", "click", "not_interested"]


@dataclass
class ReviewActivityCommand:
    user_id: int
    movie_id: int
    action_type: ReviewActivityType

    @classmethod
    def from_schema(cls, payload: ReviewActivityCreateSchema) -> ReviewActivityCommand:
        return cls(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            action_type=payload.action_type,
        )


@dataclass
class RatingReviewCommand:
    user_id: int
    movie_id: int
    rating: float
    body: str = ""

    @classmethod
    def from_schema(cls, payload: ReviewCreateSchema) -> RatingReviewCommand:
        return cls(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            rating=payload.rating,
            body=payload.body,
        )


@dataclass
class RatingReviewUpdateCommand:
    rating: float | None = None
    body: str | None = None

    @classmethod
    def from_schema(cls, payload: ReviewUpdateSchema) -> RatingReviewUpdateCommand:
        return cls(rating=payload.rating, body=payload.body)


@dataclass
class ReviewActivityDto:
    id: int
    user_id: int
    movie_id: int
    action_type: str
    action_at: datetime
    rating: float | None = None
    body: str | None = None

    @classmethod
    def from_orm(cls, row: MovaReview) -> ReviewActivityDto:
        return cls(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            action_type=row.action_type,
            action_at=row.action_at,
            rating=row.rating,
            body=row.body,
        )

    def to_schema(self) -> ReviewActivitySchema:
        from mova.adapter.inbound.api.schemas.reviews_schema import ReviewActivitySchema

        return ReviewActivitySchema(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id,
            action_type=self.action_type,
            action_at=self.action_at,
            rating=self.rating,
            body=self.body,
        )


@dataclass
class RatingReviewDto:
    id: int
    user_id: int
    movie_id: int
    rating: float
    body: str
    created_at: datetime

    @classmethod
    def from_orm(cls, row: MovaReview) -> RatingReviewDto:
        return cls(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            rating=float(row.rating or 0),
            body=row.body or "",
            created_at=row.action_at,
        )

    def to_schema(self) -> ReviewSchema:
        from mova.adapter.inbound.api.schemas.reviews_schema import ReviewSchema

        return ReviewSchema(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id,
            rating=self.rating,
            body=self.body,
            created_at=self.created_at,
        )


@dataclass
class ReviewActivityWithMovieDto:
    id: int
    user_id: int
    movie_id: int
    action_type: str
    action_at: datetime
    movie_title: str
    movie_slug: str
    rating: float | None = None
    body: str | None = None

    @classmethod
    def from_rows(cls, row: MovaReview, movie: MovaMovie) -> ReviewActivityWithMovieDto:
        return cls(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            action_type=row.action_type,
            action_at=row.action_at,
            movie_title=movie.title,
            movie_slug=movie.slug,
            rating=row.rating,
            body=row.body,
        )

    def to_schema(self) -> ReviewActivityWithMovieSchema:
        from mova.adapter.inbound.api.schemas.reviews_schema import ReviewActivityWithMovieSchema

        return ReviewActivityWithMovieSchema(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id,
            action_type=self.action_type,
            action_at=self.action_at,
            movie_title=self.movie_title,
            movie_slug=self.movie_slug,
            rating=self.rating,
            body=self.body,
        )


@dataclass
class ReviewWithUserDto:
    id: int
    user_id: int
    nickname: str
    movie_id: int
    rating: float
    body: str
    created_at: datetime

    @classmethod
    def from_rows(cls, review: MovaReview, nickname: str) -> ReviewWithUserDto:
        return cls(
            id=review.id,
            user_id=review.user_id,
            nickname=nickname,
            movie_id=review.movie_id,
            rating=float(review.rating or 0),
            body=review.body or "",
            created_at=review.action_at,
        )

    def to_schema(self) -> ReviewWithUserSchema:
        from mova.adapter.inbound.api.schemas.reviews_schema import ReviewWithUserSchema

        return ReviewWithUserSchema(
            id=self.id,
            user_id=self.user_id,
            nickname=self.nickname,
            movie_id=self.movie_id,
            rating=self.rating,
            body=self.body,
            created_at=self.created_at,
        )


@dataclass
class MovieRatingSummaryDto:
    movie_id: int
    average_rating: float
    review_count: int

    def to_schema(self) -> MovieRatingSummarySchema:
        from mova.adapter.inbound.api.schemas.reviews_schema import MovieRatingSummarySchema

        return MovieRatingSummarySchema(
            movie_id=self.movie_id,
            average_rating=self.average_rating,
            review_count=self.review_count,
        )
