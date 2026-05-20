from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from mova.app.models.base import MovaModel


class MovaChatIntent(MovaModel):
    """Mova 채팅에서 추출한 취향·검색 의도 (정제 문구). PK `id`."""

    __tablename__ = "chat_intents"

    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    refined_query: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    keywords: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    hit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_used_at: Mapped[datetime] = mapped_column(
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
