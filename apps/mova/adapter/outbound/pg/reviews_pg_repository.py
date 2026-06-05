from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.orm.reviews_orm import (
    ACTION_REVIEW,
    EVENT_ACTION_TYPES,
    MovaReview,
)
from mova.adapter.outbound.pg.pg_session import run_pg
from viewer.app.dtos.user_model import get_secom_user_nicknames, secom_user_exists

logger = logging.getLogger(__name__)


class ReviewsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


from mova.app.dtos.reviews_dto import RatingReviewCommand, ReviewActivityCommand
from mova.app.ports.output.reviews_repository import ReviewsRepository


class ReviewsPgRepository(ReviewsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def _sync_movie_rating(self, session, movie_id: int) -> tuple[float, int]:
        result = await session.execute(
            select(func.avg(MovaReview.rating), func.count(MovaReview.id)).where(
                MovaReview.movie_id == movie_id,
                MovaReview.action_type == ACTION_REVIEW,
                MovaReview.rating.is_not(None),
            ),
        )
        avg_val, count = result.one()
        average = round(float(avg_val or 0), 1)
        count_int = int(count or 0)

        movie = await session.get(MovaMovie, movie_id)
        if movie is not None:
            movie.rating = average

        return average, count_int

    async def record_activity(
        self,
        command: ReviewActivityCommand,
        action_at: datetime | None = None,
    ) -> MovaReview:
        normalized = command.action_type.strip().lower()
        user_id = command.user_id
        movie_id = command.movie_id
        if normalized not in EVENT_ACTION_TYPES:
            raise ReviewsRepositoryError(
                "action_type은 favorite, watched, click, not_interested 중 하나여야 합니다. "
                "별점 리뷰는 POST /mova/reviews 를 사용하세요.",
                status_code=400,
            )

        logger.info(
            "[ReviewsPgRepository] record_activity — user=%s movie=%s action=%s",
            user_id,
            movie_id,
            normalized,
        )

        async def work(session: AsyncSession) -> MovaReview:
            if not await secom_user_exists(user_id):
                raise ReviewsRepositoryError(
                    f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)",
                    status_code=404,
                )
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            when = action_at or datetime.now(timezone.utc)
            row = MovaReview(
                user_id=user_id,
                movie_id=movie_id,
                action_type=normalized,
                action_at=when,
            )
            session.add(row)
            await session.flush()
            await session.refresh(row)
            return row

        return await run_pg(self._session, work)

    async def upsert_rating_review(
        self,
        command: RatingReviewCommand,
    ) -> tuple[MovaReview, float, int]:
        user_id = command.user_id
        movie_id = command.movie_id
        rating = command.rating
        body = command.body
        if rating < 1 or rating > 5:
            raise ReviewsRepositoryError("별점은 1~5 사이여야 합니다.", status_code=400)

        logger.info(
            "[ReviewsPgRepository] upsert_rating_review — user=%s movie=%s rating=%s",
            user_id,
            movie_id,
            rating,
        )
        if not await secom_user_exists(user_id):
            raise ReviewsRepositoryError(
                f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)",
                status_code=404,
            )

        async def work(session: AsyncSession) -> tuple[MovaReview, float, int]:
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(MovaReview).where(
                    MovaReview.user_id == user_id,
                    MovaReview.movie_id == movie_id,
                    MovaReview.action_type == ACTION_REVIEW,
                ),
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaReview(
                    user_id=user_id,
                    movie_id=movie_id,
                    action_type=ACTION_REVIEW,
                    rating=float(rating),
                    body=body.strip(),
                )
                session.add(row)
            else:
                row.rating = float(rating)
                row.body = body.strip()

            try:
                await session.flush()
                average, count = await self._sync_movie_rating(session, movie_id)
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise ReviewsRepositoryError(
                    "리뷰 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row, average, count

        return await run_pg(self._session, work)

    async def get_rating_review_by_id(self, review_id: int) -> MovaReview | None:
        async def work(session: AsyncSession) -> MovaReview | None:
            row = await session.get(MovaReview, review_id)
            if row is None or row.action_type != ACTION_REVIEW:
                return None
            return row

        return await run_pg(self._session, work)

    async def list_activities_by_user(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[MovaReview]:
        async def work(session: AsyncSession) -> list[MovaReview]:
            if not await secom_user_exists(user_id):
                raise ReviewsRepositoryError(
                    f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)",
                    status_code=404,
                )
            stmt = (
                select(MovaReview)
                .where(
                    MovaReview.user_id == user_id,
                    MovaReview.action_type != ACTION_REVIEW,
                )
                .order_by(MovaReview.action_at.desc())
                .limit(limit)
            )
            if action_type:
                stmt = stmt.where(
                    MovaReview.action_type == action_type.strip().lower(),
                )
            result = await session.execute(stmt)
            return list(result.scalars().all())

        return await run_pg(self._session, work)

    async def list_activities_by_user_with_movies(
        self,
        user_id: int,
        *,
        action_type: str | None = None,
        limit: int = 100,
    ) -> list[tuple[MovaReview, MovaMovie]]:
        async def work(session: AsyncSession) -> list[tuple[MovaReview, MovaMovie]]:
            if not await secom_user_exists(user_id):
                raise ReviewsRepositoryError(
                    f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)",
                    status_code=404,
                )
            stmt = (
                select(MovaReview, MovaMovie)
                .join(MovaMovie, MovaReview.movie_id == MovaMovie.id)
                .where(
                    MovaReview.user_id == user_id,
                    MovaReview.action_type != ACTION_REVIEW,
                )
                .order_by(MovaReview.action_at.desc())
                .limit(limit)
            )
            if action_type:
                stmt = stmt.where(
                    MovaReview.action_type == action_type.strip().lower(),
                )
            result = await session.execute(stmt)
            return [(row[0], row[1]) for row in result.all()]

        return await run_pg(self._session, work)

    async def list_rating_reviews_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[tuple[MovaReview, str]]:
        async def work(session: AsyncSession) -> list[MovaReview]:
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaReview)
                .where(
                    MovaReview.movie_id == movie_id,
                    MovaReview.action_type == ACTION_REVIEW,
                )
                .order_by(MovaReview.action_at.desc())
                .limit(limit),
            )
            return list(result.scalars().all())

        reviews = await run_pg(self._session, work)
        nicknames = await get_secom_user_nicknames({r.user_id for r in reviews})
        return [
            (review, nicknames.get(review.user_id, "회원"))
            for review in reviews
        ]

    async def list_rating_reviews_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[MovaReview]:
        if not await secom_user_exists(user_id):
            raise ReviewsRepositoryError(
                f"회원 ID {user_id}를 찾을 수 없습니다. (Secom users)",
                status_code=404,
            )

        async def work(session: AsyncSession) -> list[MovaReview]:
            result = await session.execute(
                select(MovaReview)
                .where(
                    MovaReview.user_id == user_id,
                    MovaReview.action_type == ACTION_REVIEW,
                )
                .order_by(MovaReview.action_at.desc())
                .limit(limit),
            )
            return list(result.scalars().all())

        return await run_pg(self._session, work)

    async def get_movie_rating_summary(self, movie_id: int) -> tuple[float, int]:
        async def work(session: AsyncSession) -> tuple[float, int]:
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(func.avg(MovaReview.rating), func.count(MovaReview.id)).where(
                    MovaReview.movie_id == movie_id,
                    MovaReview.action_type == ACTION_REVIEW,
                    MovaReview.rating.is_not(None),
                ),
            )
            avg_val, count = result.one()
            return round(float(avg_val or 0), 1), int(count or 0)

        return await run_pg(self._session, work)
