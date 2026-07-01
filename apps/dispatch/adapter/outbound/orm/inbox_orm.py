from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.matrix.grid_neo_theone_base import Base


class DispatchInboxOrm(Base):
    __tablename__ = "dispatch_inbox"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender: Mapped[str] = mapped_column(Text, nullable=False, default="")
    subject: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    received_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
