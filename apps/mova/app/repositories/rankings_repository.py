import logging
from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from database import get_session_factory
from mova.app.models.movies_model import MovaMovie
from mova.app.models.rankings_model import MovaRanking

logger = logging.getLogger(__name__)


class RankingsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class RankingsRepository:
    async def replace_rankings(
        self,
        items: list[dict],
        ranked_at: date,
    ) -> list[tuple[MovaRanking, MovaMovie]]:
        if not items:
            raise RankingsRepositoryError("랭킹 목록이 비어 있습니다.", status_code=400)

        ranks = [int(i["rank"]) for i in items]
        if len(ranks) != len(set(ranks)):
            raise RankingsRepositoryError("랭킹 순위(rank)가 중복되었습니다.", status_code=400)

        movie_ids = [int(i["movie_id"]) for i in items]
        logger.info(
            "[RankingsRepository] replace_rankings — date=%s count=%s",
            ranked_at,
            len(items),
        )

        factory = get_session_factory()
        async with factory() as session:
            for mid in set(movie_ids):
                result = await session.execute(select(MovaMovie).where(MovaMovie.id == mid))
                if result.scalar_one_or_none() is None:
                    raise RankingsRepositoryError(
                        f"영화 ID {mid}를 찾을 수 없습니다.",
                        status_code=404,
                    )

            await session.execute(
                delete(MovaRanking).where(MovaRanking.ranked_at == ranked_at),
            )
            rows: list[MovaRanking] = []
            for item in items:
                row = MovaRanking(
                    rank=int(item["rank"]),
                    movie_id=int(item["movie_id"]),
                    badge=item.get("badge"),
                    ranked_at=ranked_at,
                )
                session.add(row)
                rows.append(row)

            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                raise RankingsRepositoryError(
                    "랭킹 저장에 실패했습니다.",
                    status_code=409,
                ) from e

            out: list[tuple[MovaRanking, MovaMovie]] = []
            for row in sorted(rows, key=lambda r: r.rank):
                await session.refresh(row)
                movie = await session.get(MovaMovie, row.movie_id)
                if movie is None:
                    raise RankingsRepositoryError(
                        f"영화 ID {row.movie_id}를 찾을 수 없습니다.",
                        status_code=404,
                    )
                out.append((row, movie))
            return out

    async def list_rankings_with_movies(
        self,
        *,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[tuple[MovaRanking, MovaMovie]]:
        factory = get_session_factory()
        async with factory() as session:
            stmt = (
                select(MovaRanking, MovaMovie)
                .join(MovaMovie, MovaRanking.movie_id == MovaMovie.id)
                .order_by(MovaRanking.rank.asc())
                .limit(limit)
            )
            if ranked_at is not None:
                stmt = stmt.where(MovaRanking.ranked_at == ranked_at)
            else:
                latest = await session.execute(
                    select(MovaRanking.ranked_at).order_by(MovaRanking.ranked_at.desc()).limit(1),
                )
                latest_date = latest.scalar_one_or_none()
                if latest_date is None:
                    return []
                stmt = stmt.where(MovaRanking.ranked_at == latest_date)

            result = await session.execute(stmt)
            return [(row[0], row[1]) for row in result.all()]
