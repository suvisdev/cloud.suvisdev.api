from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.oracle_database import TitanicBase
from titanic.app.dtos.james_dto import BookingCommand


class Booking(TitanicBase):
    """BookingCommand → titanic_bookings (ENTITY_RULE: int PK `id`)."""

    __tablename__ = "titanic_bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("titanic_persons.id"),
        nullable=False,
        index=True,
    )
    pclass: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    ticket: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    fare: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    cabin: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    embarked: Mapped[str] = mapped_column(String(8), nullable=False, default="")

    person: Mapped["Person"] = relationship(back_populates="bookings")

    @classmethod
    def from_command(cls, command: BookingCommand, *, person_id: int) -> Booking:
        return cls(
            person_id=person_id,
            pclass=command.pclass,
            ticket=command.ticket,
            fare=command.fare,
            cabin=command.cabin,
            embarked=command.embarked,
        )
