from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.oracle_database import TitanicBase
from titanic.app.dtos.james_dto import PersonCommand


class Person(TitanicBase):
    """PersonCommand → titanic_persons (ENTITY_RULE: int PK `id`)."""

    __tablename__ = "titanic_persons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    passenger_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    age: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    sib_sp: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    parch: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    survived: Mapped[str] = mapped_column(String(8), nullable=False, default="")

    bookings: Mapped[list["Booking"]] = relationship(back_populates="person")

    @classmethod
    def from_command(cls, command: PersonCommand) -> Person:
        return cls(
            passenger_id=command.passenger_id,
            name=command.name,
            gender=command.gender,
            age=command.age,
            sib_sp=command.sib_sp,
            parch=command.parch,
            survived=command.survived,
        )
