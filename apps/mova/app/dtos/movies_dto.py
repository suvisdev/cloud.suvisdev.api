from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.movies_schema import (
        MovieCreateSchema,
        MovieSchema,
        MovieTitleCreateSchema,
        MovieTitleSchema,
    )
    from mova.adapter.inbound.api.schemas.search_schema import (
        MovaTitleCastSchema,
        MovaTitleDetailSchema,
    )
    from mova.adapter.outbound.orm.movies_orm import MovaMovie
    from mova.app.dtos.movie_import_dto import MoviePayloadCommand


@dataclass
class MovieUpsertCommand:
    title: str
    slug: str | None = None
    release_year: str = ""
    rating: float = 0.0
    poster: str = ""
    platform: Literal["netflix", "disney"] | None = None
    genres: list[str] = field(default_factory=list)

    @classmethod
    def from_schema(cls, payload: MovieCreateSchema) -> MovieUpsertCommand:
        return cls(
            title=payload.title,
            slug=payload.slug,
            release_year=payload.release_year,
            rating=payload.rating,
            poster=payload.poster,
            platform=payload.platform,
            genres=list(payload.genres or []),
        )

    @classmethod
    def from_payload(cls, payload: MoviePayloadCommand) -> MovieUpsertCommand:
        return cls(
            title=payload.title,
            slug=payload.slug,
            release_year=payload.release_year,
            rating=payload.rating,
            poster=payload.poster,
            genres=list(payload.genres),
        )


@dataclass
class MovieTitleCommand:
    title: str

    @classmethod
    def from_schema(cls, payload: MovieTitleCreateSchema) -> MovieTitleCommand:
        return cls(title=payload.title.strip())


@dataclass
class MovieTitleDto:
    id: int
    title: str

    def to_schema(self) -> MovieTitleSchema:
        from mova.adapter.inbound.api.schemas.movies_schema import MovieTitleSchema

        return MovieTitleSchema(id=self.id, title=self.title)


@dataclass
class MovieDto:
    id: int
    slug: str
    title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None
    genres: list[str]

    @classmethod
    def from_orm(cls, row: MovaMovie) -> MovieDto:
        return cls(
            id=row.id,
            slug=row.slug,
            title=row.title,
            release_year=row.release_year or "",
            rating=float(row.rating or 0),
            poster=row.poster_url or "",
            platform=row.platform,
            genres=list(row.genres or []),
        )

    def to_schema(self) -> MovieSchema:
        from mova.adapter.inbound.api.schemas.movies_schema import MovieSchema

        return MovieSchema(
            id=self.id,
            slug=self.slug,
            title=self.title,
            release_year=self.release_year,
            rating=self.rating,
            poster=self.poster,
            platform=self.platform,
            genres=self.genres,
        )

    def to_title_schema(self) -> MovieTitleSchema:
        from mova.adapter.inbound.api.schemas.movies_schema import MovieTitleSchema

        return MovieTitleSchema(id=self.id, title=self.title)


@dataclass
class TitleCastDto:
    name: str
    role: str
    photo: str = ""

    def to_schema(self) -> MovaTitleCastSchema:
        from mova.adapter.inbound.api.schemas.search_schema import MovaTitleCastSchema

        return MovaTitleCastSchema(name=self.name, role=self.role, photo=self.photo)


@dataclass
class TitleDetailDto:
    id: str
    title: str
    year: str
    genres: list[str]
    platform: str | None
    poster: str
    backdrop: str
    rating: float
    rating_count: int
    cast: list[TitleCastDto]

    def to_schema(self) -> MovaTitleDetailSchema:
        from mova.adapter.inbound.api.schemas.search_schema import MovaTitleDetailSchema

        return MovaTitleDetailSchema(
            id=self.id,
            title=self.title,
            year=self.year,
            genres=self.genres,
            platform=self.platform,
            poster=self.poster,
            backdrop=self.backdrop,
            rating=self.rating,
            ratingCount=self.rating_count,
            cast=[item.to_schema() for item in self.cast],
        )
