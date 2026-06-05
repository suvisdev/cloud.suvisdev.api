from __future__ import annotations

from abc import ABC, abstractmethod

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


class ReviewsUseCase(ABC):
    """리뷰·활동(reviews) 입력 포트."""

    @abstractmethod
    async def record_activity(
        self,
        payload: ReviewActivityCreateSchema,
    ) -> ReviewActivitySchema:
        pass

    @abstractmethod
    async def save_rating_review(self, payload: ReviewCreateSchema) -> ReviewSchema:
        pass

    @abstractmethod
    async def update_rating_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> ReviewSchema:
        pass

    @abstractmethod
    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivitySchema]:
        pass

    @abstractmethod
    async def list_activities_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivityWithMovieSchema]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        pass

    @abstractmethod
    async def list_rating_reviews(
        self,
        *,
        user_id: int | None = None,
        movie_id: int | None = None,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_movie_with_users(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewWithUserSchema]:
        pass

    @abstractmethod
    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummarySchema:
        pass
