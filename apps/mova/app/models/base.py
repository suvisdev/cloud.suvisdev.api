"""@see docs/DevOps/Backend/ENTITY_RULE.md — mova 테이블 공통 int PK `id`."""

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class MovaModel(Base):
    """모든 mova ORM 테이블의 추상 베이스 — PK: int 자동 증감 `id`."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
