from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.orm.reviews_orm import MovaReview


class ReviewsRepository(ABC):
    """리뷰·활동(reviews) 아웃바운드 포트."""

    @abstractmethod
    async def record_activity(
        self,
        *,
        user_id: int,
        movie_id: int,
        action_type: str,
        action_at: datetime | None = None,
    ) -> MovaReview:
        pass

    @abstractmethod
    async def upsert_rating_review(
        self,
        *,
        user_id: int,
        movie_id: int,
        rating: float,
        body: str,
    ) -> tuple[MovaReview, float, int]:
        pass

    @abstractmethod
    async def get_rating_review_by_id(self, review_id: int) -> MovaReview | None:
        pass

    @abstractmethod
    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[MovaReview]:
        pass

    @abstractmethod
    async def list_activities_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[tuple[MovaReview, MovaMovie]]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[tuple[MovaReview, str]]:
        pass

    @abstractmethod
    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[MovaReview]:
        pass

    @abstractmethod
    async def get_movie_rating_summary(self, movie_id: int) -> tuple[float, int]:
        pass
