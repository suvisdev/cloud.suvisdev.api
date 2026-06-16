"""랭킹 PgRepository — RankingsRepositoryPort 구현체."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mova.adapter.outbound.orm.market_chat_orm import MovaChat
from mova.adapter.outbound.orm.market_rankings_orm import MovaRanking
from mova.adapter.outbound.orm.studio_movies_orm import MovaMovie
from mova.app.dtos.market_rankings_dto import RankingItemDto, RankingListDto
from mova.app.ports.output.market_rankings_repository import RankingsRepositoryPort

logger = logging.getLogger(__name__)


class RankingsPgRepository(RankingsRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_hot(self, source: str, limit: int) -> RankingListDto:
        rows = (
            await self._session.execute(
                select(MovaRanking, MovaMovie, MovaChat)
                .join(MovaMovie, MovaRanking.movie_id == MovaMovie.id)
                .outerjoin(MovaChat, MovaRanking.chat_id == MovaChat.id)
                .where(MovaRanking.source == source)
                .order_by(MovaRanking.ranked_at.desc(), MovaRanking.rank.asc())
                .limit(limit)
            )
        ).all()

        items = [
            RankingItemDto(
                id=r.id,
                rank=r.rank,
                movie_id=r.movie_id,
                chat_id=r.chat_id,
                source=r.source,
                score=r.score,
                badge=r.badge,
                ranked_at=r.ranked_at,
                refined_query=c.refined_query if c else None,
                slug=m.slug,
                title=m.title,
                release_year=m.release_year or "",
                rating=float(m.rating or 0),
                poster=m.poster_url or "",
                genres=list(m.genres or []),
            )
            for r, m, c in rows
        ]
        logger.debug("[RankingsPgRepository] get_hot source=%s count=%d", source, len(items))
        return RankingListDto(items=items, source=source)
