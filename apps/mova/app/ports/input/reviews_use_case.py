from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.reviews_schema import (
    ReviewActivityCreateSchema,
    ReviewCreateSchema,
    ReviewUpdateSchema,
)
from mova.app.dtos.reviews_dto import (
    MovieRatingSummaryDto,
    RatingReviewDto,
    ReviewActivityDto,
    ReviewActivityWithMovieDto,
    ReviewWithUserDto,
)


class ReviewsUseCase(ABC):
    """리뷰·활동(reviews) 입력 포트."""

    @abstractmethod
    async def record_activity(
        self,
        payload: ReviewActivityCreateSchema,
    ) -> ReviewActivityDto:
        pass

    @abstractmethod
    async def save_rating_review(self, payload: ReviewCreateSchema) -> RatingReviewDto:
        pass

    @abstractmethod
    async def update_rating_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> RatingReviewDto:
        pass

    @abstractmethod
    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivityDto]:
        pass

    @abstractmethod
    async def list_activities_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivityWithMovieDto]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[RatingReviewDto]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[RatingReviewDto]:
        pass

    @abstractmethod
    async def list_rating_reviews(
        self,
        *,
        user_id: int | None = None,
        movie_id: int | None = None,
        limit: int = 50,
    ) -> list[RatingReviewDto]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_movie_with_users(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewWithUserDto]:
        pass

    @abstractmethod
    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummaryDto:
        pass
