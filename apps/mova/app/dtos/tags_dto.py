from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.tags_schema import (
        MoviesByTagSchema,
        TagCatalogSchema,
        TagCreateSchema,
        TagSchema,
    )
    from mova.adapter.outbound.orm.movies_orm import MovaMovie
    from mova.adapter.outbound.orm.tags_orm import MovaTag


@dataclass
class TagAttachCommand:
    movie_id: int
    label: str
    slug: str | None = None
    description: str = ""
    character_id: int | None = None
    tag_kind: str = "mood"

    @classmethod
    def from_schema(cls, payload: TagCreateSchema) -> TagAttachCommand:
        return cls(
            movie_id=payload.movie_id,
            label=payload.label,
            slug=payload.slug,
            description=payload.description,
            character_id=payload.character_id,
            tag_kind=payload.tag_kind,
        )


@dataclass
class TagDto:
    id: int
    movie_id: int
    character_id: int | None
    tag_kind: str
    slug: str
    label: str
    description: str

    @classmethod
    def from_orm(cls, row: MovaTag) -> TagDto:
        return cls(
            id=row.id,
            movie_id=row.movie_id,
            character_id=row.character_id,
            tag_kind=row.tag_kind or "mood",
            slug=row.slug,
            label=row.label,
            description=row.description or "",
        )

    def to_schema(self) -> TagSchema:
        from mova.adapter.inbound.api.schemas.tags_schema import TagSchema

        return TagSchema(
            id=self.id,
            movie_id=self.movie_id,
            character_id=self.character_id,
            tag_kind=self.tag_kind,
            slug=self.slug,
            label=self.label,
            description=self.description,
        )


@dataclass
class TagCatalogDto:
    slug: str
    label: str
    description: str = ""

    @classmethod
    def from_orm(cls, row: MovaTag) -> TagCatalogDto:
        return cls(
            slug=row.slug,
            label=row.label,
            description=row.description or "",
        )

    def to_schema(self) -> TagCatalogSchema:
        from mova.adapter.inbound.api.schemas.tags_schema import TagCatalogSchema

        return TagCatalogSchema(
            slug=self.slug,
            label=self.label,
            description=self.description,
        )


@dataclass
class MovieByTagDto:
    tag_id: int
    movie_id: int
    slug: str
    tag_slug: str
    tag_label: str
    title: str
    release_year: str
    poster: str

    @classmethod
    def from_rows(cls, tag: MovaTag, movie: MovaMovie) -> MovieByTagDto:
        return cls(
            tag_id=tag.id,
            movie_id=movie.id,
            slug=movie.slug,
            tag_slug=tag.slug,
            tag_label=tag.label,
            title=movie.title,
            release_year=movie.release_year or "",
            poster=movie.poster_url or "",
        )

    def to_schema(self) -> MoviesByTagSchema:
        from mova.adapter.inbound.api.schemas.tags_schema import MoviesByTagSchema

        return MoviesByTagSchema(
            tag_id=self.tag_id,
            movie_id=self.movie_id,
            slug=self.slug,
            tag_slug=self.tag_slug,
            tag_label=self.tag_label,
            title=self.title,
            release_year=self.release_year,
            poster=self.poster,
        )
