import logging

from mova.app.schemas.reviews_schema import (
    MovieRatingSummarySchema,
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

    async def save_review(self, payload: ReviewCreateSchema) -> ReviewSchema:
        logger.info("[ReviewsController] save_review — movie=%s", payload.movie_id)
        return await self.service.save_review(payload)

    async def update_review(
        self,
        review_id: int,
        payload: ReviewUpdateSchema,
    ) -> ReviewSchema:
        return await self.service.update_review(review_id, payload)

    async def list_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewSchema]:
        return await self.service.list_reviews_by_movie(movie_id, limit=limit)

    async def list_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[ReviewWithUserSchema]:
        return await self.service.list_by_movie(movie_id, limit=limit)

    async def list_by_user(self, user_id: int, limit: int = 50) -> list[ReviewSchema]:
        return await self.service.list_by_user(user_id, limit=limit)

    async def get_movie_rating_summary(self, movie_id: int) -> MovieRatingSummarySchema:
        return await self.service.get_movie_rating_summary(movie_id)
