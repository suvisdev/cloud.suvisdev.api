from __future__ import annotations

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
from mova.adapter.outbound.pg.reviews_pg_repository import ReviewsRepositoryError
from mova.app.ports.input.reviews_use_case import ReviewsUseCase
from mova.app.ports.output.reviews_repository import ReviewsRepository


class ReviewsInteractor(ReviewsUseCase):
    def __init__(self, repository: ReviewsRepository) -> None:
        self._repository = repository

    def _activity_schema(self, row) -> ReviewActivitySchema:
        return ReviewActivitySchema(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            action_type=row.action_type,
            action_at=row.action_at,
            rating=row.rating,
            body=row.body,
        )

    def _rating_review_schema(self, row) -> ReviewSchema:
        return ReviewSchema(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            rating=float(row.rating or 0),
            body=row.body or "",
            created_at=row.action_at,
        )

    async def record_activity(
        self,
        payload: ReviewActivityCreateSchema,
    ) -> ReviewActivitySchema:
        row = await self._repository.record_activity(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            action_type=payload.action_type,
        )
        return self._activity_schema(row)

    async def save_rating_review(self, payload: ReviewCreateSchema) -> ReviewSchema:
        row, _, _ = await self._repository.upsert_rating_review(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            rating=payload.rating,
            body=payload.body,
        )
        return self._rating_review_schema(row)

    async def update_rating_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> ReviewSchema:
        row = await self._repository.get_rating_review_by_id(review_id)
        if row is None:
            raise ReviewsRepositoryError(
                f"리뷰 ID {review_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        rating = payload.rating if payload.rating is not None else float(row.rating or 0)
        body = payload.body if payload.body is not None else (row.body or "")
        updated, _, _ = await self._repository.upsert_rating_review(
            user_id=row.user_id,
            movie_id=row.movie_id,
            rating=rating,
            body=body,
        )
        return self._rating_review_schema(updated)

    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivitySchema]:
        rows = await self._repository.list_activities_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )
        return [self._activity_schema(row) for row in rows]

    async def list_activities_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivityWithMovieSchema]:
        rows = await self._repository.list_activities_by_user_with_movies(
            user_id,
            action_type=action_type,
            limit=limit,
        )
        return [
            ReviewActivityWithMovieSchema(
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
            for row, movie in rows
        ]

    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        rows = await self._repository.list_rating_reviews_by_movie(movie_id, limit=limit)
        return [self._rating_review_schema(review) for review, _nickname in rows]

    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        rows = await self._repository.list_rating_reviews_by_user(user_id, limit=limit)
        return [self._rating_review_schema(row) for row in rows]

    async def list_rating_reviews(
        self,
        *,
        user_id: int | None = None,
        movie_id: int | None = None,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        if user_id is None and movie_id is None:
            raise ReviewsRepositoryError(
                "user_id 또는 movie_id가 필요합니다.",
                status_code=400,
            )
        if user_id is not None:
            return await self.list_rating_reviews_by_user(user_id, limit=limit)
        return await self.list_rating_reviews_by_movie(movie_id, limit=limit)

    async def list_rating_reviews_by_movie_with_users(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewWithUserSchema]:
        rows = await self._repository.list_rating_reviews_by_movie(movie_id, limit=limit)
        return [
            ReviewWithUserSchema(
                id=review.id,
                user_id=review.user_id,
                nickname=nickname,
                movie_id=review.movie_id,
                rating=float(review.rating or 0),
                body=review.body or "",
                created_at=review.action_at,
            )
            for review, nickname in rows
        ]

    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummarySchema:
        average, count = await self._repository.get_movie_rating_summary(movie_id)
        return MovieRatingSummarySchema(
            movie_id=movie_id,
            average_rating=average,
            review_count=count,
        )
