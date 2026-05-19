from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class MovaSearchQuery(Base):
    """사용자가 입력한 검색어 집계."""

    __tablename__ = "mova_search_queries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    search_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
