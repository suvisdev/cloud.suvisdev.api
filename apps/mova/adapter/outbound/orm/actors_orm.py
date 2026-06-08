"""@see docs/DevOps/suvisdev/ENTITY_RULE.md — 인물(감독·배우) 정보."""

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mova.adapter.outbound.orm.base_orm import MovaModel


class MovaActor(MovaModel):
    """인물 정보. PK `id` — 역할은 `role_type`(director|actor)."""

    __tablename__ = "actors"
    __table_args__ = (
        UniqueConstraint("name", "role_type", name="uq_actors_name_role"),
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    role_type: Mapped[str] = mapped_column(String(16), nullable=False, default="actor", index=True)
    profile_photo_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
