from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MovaTitle(Base):
    __tablename__ = "mova_titles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    year: Mapped[str] = mapped_column(String(8), nullable=False)
    genres: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    country: Mapped[str] = mapped_column(String(64), nullable=False)
    age_rating: Mapped[str] = mapped_column(String(16), nullable=False)
    rank_badge: Mapped[str | None] = mapped_column(String(255), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(16), nullable=True)
    poster_url: Mapped[str] = mapped_column(Text, nullable=False)
    backdrop_url: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    search_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    badge: Mapped[str | None] = mapped_column(String(8), nullable=True)
    synopsis: Mapped[str] = mapped_column(Text, nullable=False, default="")
    rating_distribution: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    gallery: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    comments: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    people: Mapped[list["MovaPerson"]] = relationship(back_populates="title", cascade="all, delete-orphan")
    keywords: Mapped[list["MovaKeyword"]] = relationship(
        back_populates="title",
        cascade="all, delete-orphan",
    )


class MovaPerson(Base):
    __tablename__ = "mova_people"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_id: Mapped[int] = mapped_column(ForeignKey("mova_titles.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    search_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    photo_url: Mapped[str] = mapped_column(Text, nullable=False, default="")

    title: Mapped["MovaTitle"] = relationship(back_populates="people")


class MovaKeyword(Base):
    __tablename__ = "mova_keywords"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title_id: Mapped[int] = mapped_column(ForeignKey("mova_titles.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    title: Mapped["MovaTitle"] = relationship(back_populates="keywords")
