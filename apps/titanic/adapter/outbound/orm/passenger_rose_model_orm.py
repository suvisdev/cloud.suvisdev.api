from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base
from titanic.app.dtos.crew_james_director_dto import BookingCommand


class RoseModelOrm(Base):
    """RoseModelCommand → bookings (ENTITY_RULE: int PK `id`)."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("passengers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pclass: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    ticket: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    fare: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    cabin: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    embarked: Mapped[str] = mapped_column(String(8), nullable=False, default="")
