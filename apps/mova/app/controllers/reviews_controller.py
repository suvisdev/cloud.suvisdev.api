import logging

from mova.app.schemas.reviews_schema import (
    MovieRatingSummarySchema,
    ReviewActivityCreateSchema,
    ReviewActivitySchema,
    ReviewActivityWithMovieSchema,
    ReviewCreateSchema,
    ReviewSchema,
    ReviewUpdateSchema,
    ReviewWithUserSchema,
)
from mova.app.services.reviews_service import ReviewsService

logger = logging.getLogger(__name__)


class ReviewsController:
    def __init__(self) -> None:
        self.service = ReviewsService()

    async def record_activity(
        self,
        payload: ReviewActivityCreateSchema,
    ) -> ReviewActivitySchema:
        logger.info(
            "[ReviewsController] record_activity — user=%s movie=%s",
            payload.user_id,
            payload.movie_id,
        )
        return await self.service.record_activity(payload)

    async def save_rating_review(self, payload: ReviewCreateSchema) -> ReviewSchema:
        logger.info(
            "[ReviewsController] save_rating_review — movie=%s",
            payload.movie_id,
        )
        return await self.service.save_rating_review(payload)

    async def update_rating_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> ReviewSchema:
        return await self.service.update_rating_review(review_id, payload)

    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
        with_movies: bool = False,
    ) -> list[ReviewActivitySchema] | list[ReviewActivityWithMovieSchema]:
        if with_movies:
            return await self.service.list_activities_by_user_with_movies(
                user_id,
                action_type=action_type,
                limit=limit,
            )
        return await self.service.list_activities_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )

    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        return await self.service.list_rating_reviews_by_movie(movie_id, limit=limit)

    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        return await self.service.list_rating_reviews_by_user(user_id, limit=limit)

    async def list_rating_reviews_by_movie_with_users(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewWithUserSchema]:
        return await self.service.list_rating_reviews_by_movie_with_users(
            movie_id,
            limit=limit,
        )

    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummarySchema:
        return await self.service.get_movie_rating_summary(movie_id)
