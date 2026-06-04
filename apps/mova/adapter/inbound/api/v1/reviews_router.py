from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

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
from mova.app.use_cases.reviews_interactor import ReviewsInteractor

reviews_router = APIRouter(tags=["mova-reviews"])

logger = logging.getLogger(__name__)


@reviews_router.post("/reviews/activity", response_model=ReviewActivitySchema, status_code=201)
async def record_review_activity(req: ReviewActivityCreateSchema) -> ReviewActivitySchema:
    logger.info(
        "[ReviewsRouter] activity — user=%s movie=%s %s",
        req.user_id,
        req.movie_id,
        req.action_type,
    )
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.record_activity(req)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.get("/reviews/activity", response_model=list[ReviewActivitySchema])
async def list_review_activities(
    user_id: int,
    action_type: str | None = None,
    limit: int = 100,
) -> list[ReviewActivitySchema]:
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.list_activities_by_user(
            user_id,
            action_type=action_type,
            limit=limit,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.get(
    "/users/{user_id}/reviews/activity",
    response_model=list[ReviewActivityWithMovieSchema],
)
async def list_user_review_activities(
    user_id: int,
    action_type: str | None = None,
    limit: int = 100,
) -> list[ReviewActivityWithMovieSchema]:
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.list_activities_by_user_with_movies(
            user_id,
            action_type=action_type,
            limit=limit,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.post("/reviews", response_model=ReviewSchema, status_code=201)
async def save_review(req: ReviewCreateSchema) -> ReviewSchema:
    logger.info("[ReviewsRouter] review — user=%s movie=%s", req.user_id, req.movie_id)
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.save_rating_review(req)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.patch("/reviews/{review_id}", response_model=ReviewSchema)
async def update_review(review_id: int, req: ReviewUpdateSchema) -> ReviewSchema:
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.update_rating_review(review_id, req)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.get("/reviews", response_model=list[ReviewSchema])
async def list_reviews(
    user_id: int | None = None,
    movie_id: int | None = None,
    limit: int = 50,
) -> list[ReviewSchema]:
    if user_id is None and movie_id is None:
        raise HTTPException(status_code=400, detail="user_id 또는 movie_id가 필요합니다.")
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        if user_id is not None:
            return await use_case.list_rating_reviews_by_user(user_id, limit=limit)
        return await use_case.list_rating_reviews_by_movie(movie_id, limit=limit)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.get(
    "/movies/{movie_id}/reviews",
    response_model=list[ReviewWithUserSchema],
)
async def list_movie_reviews(
    movie_id: int,
    limit: int = 50,
) -> list[ReviewWithUserSchema]:
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.list_rating_reviews_by_movie_with_users(
            movie_id,
            limit=limit,
        )
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@reviews_router.get(
    "/movies/{movie_id}/rating-summary",
    response_model=MovieRatingSummarySchema,
)
async def movie_rating_summary(movie_id: int) -> MovieRatingSummarySchema:
    use_case: ReviewsUseCase = ReviewsInteractor()
    try:
        return await use_case.get_movie_rating_summary(movie_id)
    except ReviewsRepositoryError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
