import logging

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from database import get_session_factory
from mova.app.models.movies_model import MovaMovie
from mova.app.models.reviews_model import MovaReview
from mova.app.models.users_model import MovaUser

logger = logging.getLogger(__name__)


class ReviewsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ReviewsRepository:
    async def _sync_movie_rating(self, session, movie_id: int) -> tuple[float, int]:
        result = await session.execute(
            select(func.avg(MovaReview.rating), func.count(MovaReview.id)).where(
                MovaReview.movie_id == movie_id,
            ),
        )
        avg_val, count = result.one()
        average = round(float(avg_val or 0), 1)
        count_int = int(count or 0)

        movie = await session.get(MovaMovie, movie_id)
        if movie is not None:
            movie.rating = average

        return average, count_int

    async def upsert_review(
        self,
        *,
        user_id: int,
        movie_id: int,
        rating: float,
        body: str,
    ) -> tuple[MovaReview, float, int]:
        if rating < 1 or rating > 5:
            raise ReviewsRepositoryError("별점은 1~5 사이여야 합니다.", status_code=400)

        logger.info(
            "[ReviewsRepository] upsert_review — user=%s movie=%s rating=%s",
            user_id,
            movie_id,
            rating,
        )
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaUser, user_id) is None:
                raise ReviewsRepositoryError(
                    f"사용자 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            result = await session.execute(
                select(MovaReview).where(
                    MovaReview.user_id == user_id,
                    MovaReview.movie_id == movie_id,
                ),
            )
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaReview(
                    user_id=user_id,
                    movie_id=movie_id,
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
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise ReviewsRepositoryError(
                    "리뷰 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row, average, count

    async def get_by_id(self, review_id: int) -> MovaReview | None:
        factory = get_session_factory()
        async with factory() as session:
            return await session.get(MovaReview, review_id)

    async def list_by_movie(
        self,
        movie_id: int,
        limit: int = 50,
    ) -> list[tuple[MovaReview, MovaUser]]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaReview, MovaUser)
                .join(MovaUser, MovaReview.user_id == MovaUser.id)
                .where(MovaReview.movie_id == movie_id)
                .order_by(MovaReview.created_at.desc())
                .limit(limit),
            )
            return [(row[0], row[1]) for row in result.all()]

    async def list_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> list[MovaReview]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaUser, user_id) is None:
                raise ReviewsRepositoryError(
                    f"사용자 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(MovaReview)
                .where(MovaReview.user_id == user_id)
                .order_by(MovaReview.created_at.desc())
                .limit(limit),
            )
            return list(result.scalars().all())

    async def get_movie_rating_summary(self, movie_id: int) -> tuple[float, int]:
        factory = get_session_factory()
        async with factory() as session:
            if await session.get(MovaMovie, movie_id) is None:
                raise ReviewsRepositoryError(
                    f"영화 ID {movie_id}를 찾을 수 없습니다.",
                    status_code=404,
                )
            result = await session.execute(
                select(func.avg(MovaReview.rating), func.count(MovaReview.id)).where(
                    MovaReview.movie_id == movie_id,
                ),
            )
            avg_val, count = result.one()
            return round(float(avg_val or 0), 1), int(count or 0)
