"""@see docs/DevOps/Backend/ENTITY_RULE.md — Mova HOT 랭킹 (영화 FK)."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel


class MovaRanking(MovaModel):
    """실시간 HOT 랭킹. PK `id` — `movie_id` FK, 기준일 `ranked_at`."""

    __tablename__ = "rankings"
    __table_args__ = (
        UniqueConstraint("rank", "ranked_at", name="uq_rankings_rank_date"),
    )

    rank: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    badge: Mapped[str | None] = mapped_column(String(8), nullable=True)
    ranked_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
