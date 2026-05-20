import logging

from mova.app.repositories.reviews_repository import ReviewsRepository, ReviewsRepositoryError
from mova.app.schemas.reviews_schema import (
    MovieRatingSummarySchema,
    ReviewCreateSchema,
    ReviewSchema,
    ReviewUpdateSchema,
    ReviewWithUserSchema,
)

logger = logging.getLogger(__name__)


class ReviewsService:
    def __init__(self) -> None:
        self.repository = ReviewsRepository()

    def _to_schema(self, row) -> ReviewSchema:
        return ReviewSchema(
            id=row.id,
            user_id=row.user_id,
            movie_id=row.movie_id,
            rating=row.rating,
            body=row.body or "",
            created_at=row.created_at,
        )

    async def save_review(self, payload: ReviewCreateSchema) -> ReviewSchema:
        logger.info(
            "[ReviewsService] save_review — user=%s movie=%s",
            payload.user_id,
            payload.movie_id,
        )
        row, _avg, _count = await self.repository.upsert_review(
            user_id=payload.user_id,
            movie_id=payload.movie_id,
            rating=payload.rating,
            body=payload.body,
        )
        return self._to_schema(row)

    async def update_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> ReviewSchema:
        row = await self.repository.get_by_id(review_id)
        if row is None:
            raise ReviewsRepositoryError(
                f"리뷰 ID {review_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        rating = payload.rating if payload.rating is not None else row.rating
        body = payload.body if payload.body is not None else row.body
        updated, _, _ = await self.repository.upsert_review(
            user_id=row.user_id,
            movie_id=row.movie_id,
            rating=rating,
            body=body,
        )
        return self._to_schema(updated)

    async def list_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        rows = await self.repository.list_by_movie(movie_id, limit=limit)
        return [self._to_schema(review) for review, _user in rows]

    async def list_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewWithUserSchema]:
        rows = await self.repository.list_by_movie(movie_id, limit=limit)
        return [
            ReviewWithUserSchema(
                id=review.id,
                user_id=review.user_id,
                nickname=user.nickname,
                movie_id=review.movie_id,
                rating=review.rating,
                body=review.body or "",
                created_at=review.created_at,
            )
            for review, user in rows
        ]

    async def list_by_user(self, user_id: int, limit: int = 50) -> list[ReviewSchema]:
        rows = await self.repository.list_by_user(user_id, limit=limit)
        return [self._to_schema(r) for r in rows]

    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummarySchema:
        average, count = await self.repository.get_movie_rating_summary(movie_id)
        return MovieRatingSummarySchema(
            movie_id=movie_id,
            average_rating=average,
            review_count=count,
        )
