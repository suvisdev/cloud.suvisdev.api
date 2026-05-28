"""James CSV 업로드 — Neon(PostgreSQL) ORM."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import TitanicBase


class TitanicPassengerRow(TitanicBase):
    """타이타닉 승객 1행 (CSV 컬럼과 동일, 문자열 저장)."""

    __tablename__ = "titanic_passengers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    passenger_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    survived: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    pclass: Mapped[str] = mapped_column(String(8), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    gender: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    age: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    sibsp: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    parch: Mapped[str] = mapped_column(String(16), nullable=False, default="")
    ticket: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    fare: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    cabin: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    embarked: Mapped[str] = mapped_column(String(8), nullable=False, default="")
