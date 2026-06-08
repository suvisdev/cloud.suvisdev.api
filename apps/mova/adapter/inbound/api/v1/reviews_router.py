from __future__ import annotations

from fastapi import APIRouter, Depends

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
from mova.app.ports.input.reviews_use_case import ReviewsUseCase
from mova.dependencies.reviews_provider import get_reviews_use_case

reviews_router = APIRouter(tags=["mova-reviews"])


@reviews_router.post("/reviews/activity", response_model=ReviewActivitySchema, status_code=201)
async def record_review_activity(
    req: ReviewActivityCreateSchema,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> ReviewActivitySchema:
    return (await reviews.record_activity(req)).to_schema()


@reviews_router.get("/reviews/activity", response_model=list[ReviewActivitySchema])
async def list_review_activities(
    user_id: int,
    action_type: str | None = None,
    limit: int = 100,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> list[ReviewActivitySchema]:
    rows = await reviews.list_activities_by_user(
        user_id,
        action_type=action_type,
        limit=limit,
    )
    return [row.to_schema() for row in rows]


@reviews_router.get(
    "/users/{user_id}/reviews/activity",
    response_model=list[ReviewActivityWithMovieSchema],
)
async def list_user_review_activities(
    user_id: int,
    action_type: str | None = None,
    limit: int = 100,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> list[ReviewActivityWithMovieSchema]:
    rows = await reviews.list_activities_by_user_with_movies(
        user_id,
        action_type=action_type,
        limit=limit,
    )
    return [row.to_schema() for row in rows]


@reviews_router.post("/reviews", response_model=ReviewSchema, status_code=201)
async def save_review(
    req: ReviewCreateSchema,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> ReviewSchema:
    return (await reviews.save_rating_review(req)).to_schema()


@reviews_router.patch("/reviews/{review_id}", response_model=ReviewSchema)
async def update_review(
    review_id: int,
    req: ReviewUpdateSchema,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> ReviewSchema:
    return (await reviews.update_rating_review(review_id, req)).to_schema()


@reviews_router.get("/reviews", response_model=list[ReviewSchema])
async def list_reviews(
    user_id: int | None = None,
    movie_id: int | None = None,
    limit: int = 50,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> list[ReviewSchema]:
    rows = await reviews.list_rating_reviews(
        user_id=user_id,
        movie_id=movie_id,
        limit=limit,
    )
    return [row.to_schema() for row in rows]


@reviews_router.get(
    "/movies/{movie_id}/reviews",
    response_model=list[ReviewWithUserSchema],
)
async def list_movie_reviews(
    movie_id: int,
    limit: int = 50,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> list[ReviewWithUserSchema]:
    rows = await reviews.list_rating_reviews_by_movie_with_users(movie_id, limit=limit)
    return [row.to_schema() for row in rows]


@reviews_router.get(
    "/movies/{movie_id}/rating-summary",
    response_model=MovieRatingSummarySchema,
)
async def movie_rating_summary(
    movie_id: int,
    reviews: ReviewsUseCase = Depends(get_reviews_use_case),
) -> MovieRatingSummarySchema:
    return (await reviews.get_movie_rating_summary(movie_id)).to_schema()
