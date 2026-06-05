from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.chat_orm import MovaChat
from mova.adapter.outbound.orm.movies_orm import MovaMovie
from mova.adapter.outbound.orm.picks_orm import MovaPick
from mova.adapter.outbound.orm.rankings_orm import MovaRanking
from mova.adapter.outbound.pg.pg_session import run_pg
from mova.domain.value_objects.ranking_source import RANKING_SOURCES
from mova.app.ports.output.rankings_repository import RankingsRepository

logger = logging.getLogger(__name__)


class RankingsRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _pick_weight(pick_rank: int) -> int:
    return max(1, 4 - int(pick_rank))


class RankingsPgRepository(RankingsRepository):
    def __init__(self, session: AsyncSession | None = None) -> None:
        self._session = session

    async def replace_rankings(
        self,
        items: list[dict],
        ranked_at: date,
        *,
        source: str,
    ) -> list[tuple[MovaRanking, MovaMovie]]:
        if source not in RANKING_SOURCES:
            raise RankingsRepositoryError(
                f"지원하지 않는 source: {source}",
                status_code=400,
            )
        if not items:
            raise RankingsRepositoryError("랭킹 목록이 비어 있습니다.", status_code=400)

        ranks = [int(i["rank"]) for i in items]
        if len(ranks) != len(set(ranks)):
            raise RankingsRepositoryError("랭킹 순위(rank)가 중복되었습니다.", status_code=400)

        movie_ids = [int(i["movie_id"]) for i in items]
        logger.info(
            "[RankingsPgRepository] replace_rankings — date=%s source=%s count=%s",
            ranked_at,
            source,
            len(items),
        )

        async def work(session: AsyncSession) -> list[tuple[MovaRanking, MovaMovie]]:
            for mid in set(movie_ids):
                result = await session.execute(select(MovaMovie).where(MovaMovie.id == mid))
                if result.scalar_one_or_none() is None:
                    raise RankingsRepositoryError(
                        f"영화 ID {mid}를 찾을 수 없습니다.",
                        status_code=404,
                    )

            await session.execute(
                delete(MovaRanking).where(
                    MovaRanking.ranked_at == ranked_at,
                    MovaRanking.source == source,
                ),
            )
            rows: list[MovaRanking] = []
            for item in items:
                row = MovaRanking(
                    rank=int(item["rank"]),
                    movie_id=int(item["movie_id"]),
                    chat_id=item.get("chat_id"),
                    source=source,
                    score=item.get("score"),
                    badge=item.get("badge"),
                    ranked_at=ranked_at,
                )
                session.add(row)
                rows.append(row)

            try:
                await session.flush()
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

        return await run_pg(self._session, work)

    async def list_rankings_with_movies(
        self,
        *,
        source: str,
        ranked_at: date | None = None,
        limit: int = 20,
    ) -> list[tuple[MovaRanking, MovaMovie, str | None]]:
        if source not in RANKING_SOURCES:
            raise RankingsRepositoryError(
                f"지원하지 않는 source: {source}",
                status_code=400,
            )

        async def work(session: AsyncSession) -> list[tuple[MovaRanking, MovaMovie, str | None]]:
            stmt = (
                select(MovaRanking, MovaMovie, MovaChat.refined_query)
                .join(MovaMovie, MovaRanking.movie_id == MovaMovie.id)
                .outerjoin(MovaChat, MovaRanking.chat_id == MovaChat.id)
                .where(MovaRanking.source == source)
                .order_by(MovaRanking.rank.asc())
                .limit(limit)
            )
            if ranked_at is not None:
                stmt = stmt.where(MovaRanking.ranked_at == ranked_at)
            else:
                latest = await session.execute(
                    select(MovaRanking.ranked_at)
                    .where(MovaRanking.source == source)
                    .order_by(MovaRanking.ranked_at.desc())
                    .limit(1),
                )
                latest_date = latest.scalar_one_or_none()
                if latest_date is None:
                    return []
                stmt = stmt.where(MovaRanking.ranked_at == latest_date)

            result = await session.execute(stmt)
            return [(row[0], row[1], row[2]) for row in result.all()]

        return await run_pg(self._session, work)

    async def aggregate_chat_trend_scores(
        self,
        *,
        since: date,
        limit: int = 10,
    ) -> list[dict]:
        since_dt = datetime.combine(since, datetime.min.time(), tzinfo=timezone.utc)

        async def work(session: AsyncSession) -> list[dict]:
            result = await session.execute(
                select(
                    MovaPick.movie_id,
                    MovaPick.chat_id,
                    MovaPick.pick_rank,
                    MovaChat.hit_count,
                )
                .join(MovaChat, MovaChat.id == MovaPick.chat_id)
                .where(MovaPick.batch_at >= since_dt),
            )
            rows = result.all()
            if not rows:
                return []

            movie_scores: dict[int, int] = {}
            movie_best_chat: dict[int, tuple[int, int]] = {}

            for movie_id, chat_id, pick_rank, hit_count in rows:
                contribution = _pick_weight(pick_rank) * max(int(hit_count or 1), 1)
                movie_scores[movie_id] = movie_scores.get(movie_id, 0) + contribution
                prev = movie_best_chat.get(movie_id)
                if prev is None or contribution > prev[1]:
                    movie_best_chat[movie_id] = (chat_id, contribution)

            ranked = sorted(movie_scores.items(), key=lambda item: item[1], reverse=True)[:limit]
            return [
                {
                    "movie_id": movie_id,
                    "score": score,
                    "chat_id": movie_best_chat[movie_id][0],
                }
                for movie_id, score in ranked
            ]

        return await run_pg(self._session, work)
