"""@see docs/DevOps/suvisdev/ENTITY_RULE.md — secom 테이블 공통 int PK `id`."""

from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.oracle_database import SecomBase


class ViewerModel(SecomBase):
    """모든 secom ORM 테이블의 추상 베이스 — PK: int 자동 증감 `id`."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
