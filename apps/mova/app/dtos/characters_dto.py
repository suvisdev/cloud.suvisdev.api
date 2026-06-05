from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mova.adapter.inbound.api.schemas.characters_schema import (
        CharacterLinkCreateSchema,
        CharacterLinkSchema,
        CharacterWithActorSchema,
        CharacterWithMovieSchema,
    )
    from mova.adapter.outbound.orm.actors_orm import MovaActor
    from mova.adapter.outbound.orm.characters_orm import MovaCharacter
    from mova.adapter.outbound.orm.movies_orm import MovaMovie


@dataclass
class CharacterLinkCommand:
    movie_id: int
    actor_id: int

    @classmethod
    def from_schema(cls, payload: CharacterLinkCreateSchema) -> CharacterLinkCommand:
        return cls(movie_id=payload.movie_id, actor_id=payload.actor_id)


@dataclass
class CharacterLinkDto:
    id: int
    movie_id: int
    actor_id: int

    @classmethod
    def from_orm(cls, row: MovaCharacter) -> CharacterLinkDto:
        return cls(id=row.id, movie_id=row.movie_id, actor_id=row.actor_id)

    def to_schema(self) -> CharacterLinkSchema:
        from mova.adapter.inbound.api.schemas.characters_schema import CharacterLinkSchema

        return CharacterLinkSchema(
            id=self.id,
            movie_id=self.movie_id,
            actor_id=self.actor_id,
        )


@dataclass
class CharacterWithActorDto:
    id: int
    movie_id: int
    actor_id: int
    actor_name: str
    role_type: str
    profile_photo: str

    @classmethod
    def from_rows(cls, link: MovaCharacter, actor: MovaActor) -> CharacterWithActorDto:
        return cls(
            id=link.id,
            movie_id=link.movie_id,
            actor_id=link.actor_id,
            actor_name=actor.name,
            role_type=actor.role_type,
            profile_photo=actor.profile_photo_url or "",
        )

    def to_schema(self) -> CharacterWithActorSchema:
        from mova.adapter.inbound.api.schemas.characters_schema import CharacterWithActorSchema

        return CharacterWithActorSchema(
            id=self.id,
            movie_id=self.movie_id,
            actor_id=self.actor_id,
            actor_name=self.actor_name,
            role_type=self.role_type,
            profile_photo=self.profile_photo,
        )


@dataclass
class CharacterWithMovieDto:
    id: int
    movie_id: int
    actor_id: int
    slug: str
    movie_title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None

    @classmethod
    def from_rows(cls, link: MovaCharacter, movie: MovaMovie) -> CharacterWithMovieDto:
        return cls(
            id=link.id,
            movie_id=link.movie_id,
            actor_id=link.actor_id,
            slug=movie.slug,
            movie_title=movie.title,
            release_year=movie.release_year or "",
            rating=float(movie.rating or 0),
            poster=movie.poster_url or "",
            platform=movie.platform,
        )

    def to_schema(self) -> CharacterWithMovieSchema:
        from mova.adapter.inbound.api.schemas.characters_schema import CharacterWithMovieSchema

        return CharacterWithMovieSchema(
            id=self.id,
            movie_id=self.movie_id,
            actor_id=self.actor_id,
            slug=self.slug,
            movie_title=self.movie_title,
            release_year=self.release_year,
            rating=self.rating,
            poster=self.poster,
            platform=self.platform,
        )
