from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from titanic.app.dtos.crew_james_director_dto import PassengerCommand
from core.matrix.grid_neo_theone_base import Base

class JackTrainerOrm(Base):
    """JackTrainerCommand → passengers (ENTITY_RULE: int PK `id`)."""

    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    passenger_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    age: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    sib_sp: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    parch: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    survived: Mapped[str] = mapped_column(String(8), nullable=False, default="")
