from __future__ import annotations

from mova.adapter.inbound.api.schemas.reviews_schema import (
    ReviewActivityCreateSchema,
    ReviewCreateSchema,
    ReviewUpdateSchema,
)
from mova.adapter.outbound.pg.reviews_pg_repository import ReviewsRepositoryError
from mova.app.dtos.reviews_dto import (
    MovieRatingSummaryDto,
    RatingReviewCommand,
    RatingReviewDto,
    RatingReviewUpdateCommand,
    ReviewActivityCommand,
    ReviewActivityDto,
    ReviewActivityWithMovieDto,
    ReviewWithUserDto,
)
from mova.app.ports.input.reviews_use_case import ReviewsUseCase
from mova.app.ports.output.reviews_repository import ReviewsRepository


class ReviewsInteractor(ReviewsUseCase):
    def __init__(self, repository: ReviewsRepository) -> None:
        self._repository = repository

    async def record_activity(
        self,
        payload: ReviewActivityCreateSchema,
    ) -> ReviewActivityDto:
        command = ReviewActivityCommand.from_schema(payload)
        row = await self._repository.record_activity(command)
        return ReviewActivityDto.from_orm(row)

    async def save_rating_review(self, payload: ReviewCreateSchema) -> RatingReviewDto:
        command = RatingReviewCommand.from_schema(payload)
        row, _, _ = await self._repository.upsert_rating_review(command)
        return RatingReviewDto.from_orm(row)

    async def update_rating_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> RatingReviewDto:
        command = RatingReviewUpdateCommand.from_schema(payload)
        row = await self._repository.get_rating_review_by_id(review_id)
        if row is None:
            raise ReviewsRepositoryError(
                f"리뷰 ID {review_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        rating = command.rating if command.rating is not None else float(row.rating or 0)
        body = command.body if command.body is not None else (row.body or "")
        updated, _, _ = await self._repository.upsert_rating_review(
            RatingReviewCommand(
                user_id=row.user_id,
                movie_id=row.movie_id,
                rating=rating,
                body=body,
            ),
        )
        return RatingReviewDto.from_orm(updated)

    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivityDto]:
        rows = await self._repository.list_activities_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )
        return [ReviewActivityDto.from_orm(row) for row in rows]

    async def list_activities_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[ReviewActivityWithMovieDto]:
        rows = await self._repository.list_activities_by_user_with_movies(
            user_id,
            action_type=action_type,
            limit=limit,
        )
        return [
            ReviewActivityWithMovieDto.from_rows(row, movie)
            for row, movie in rows
        ]

    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[RatingReviewDto]:
        rows = await self._repository.list_rating_reviews_by_movie(movie_id, limit=limit)
        return [RatingReviewDto.from_orm(review) for review, _nickname in rows]

    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[RatingReviewDto]:
        rows = await self._repository.list_rating_reviews_by_user(user_id, limit=limit)
        return [RatingReviewDto.from_orm(row) for row in rows]

    async def list_rating_reviews(
        self,
        *,
        user_id: int | None = None,
        movie_id: int | None = None,
        limit: int = 50,
    ) -> list[RatingReviewDto]:
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
    ) -> list[ReviewWithUserDto]:
        rows = await self._repository.list_rating_reviews_by_movie(movie_id, limit=limit)
        return [
            ReviewWithUserDto.from_rows(review, nickname)
            for review, nickname in rows
        ]

    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummaryDto:
        average, count = await self._repository.get_movie_rating_summary(movie_id)
        return MovieRatingSummaryDto(
            movie_id=movie_id,
            average_rating=average,
            review_count=count,
        )
