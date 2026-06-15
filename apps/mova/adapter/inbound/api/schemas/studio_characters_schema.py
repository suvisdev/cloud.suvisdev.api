from __future__ import annotations

from pydantic import BaseModel, Field


class CharacterLinkCreateSchema(BaseModel):
    movie_id: int
    actor_id: int


class CharacterLinkSchema(BaseModel):
    id: int
    movie_id: int
    actor_id: int


class CharacterWithActorSchema(BaseModel):
    id: int
    movie_id: int
    actor_id: int
    actor_name: str
    role_type: str
    profile_photo: str


class CharacterWithMovieSchema(BaseModel):
    id: int
    movie_id: int
    actor_id: int
    slug: str
    movie_title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None


class StudioCharactersSchema(BaseModel):

    id: int = Field(0, description="Characters ID")
    name: str = Field("캐스팅 감독 (Casting Director)", description="Casting Director's name")
    # 영화와 배우를 연결하는 중간자. characters 테이블로 movies ↔ actors N:M 중계

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "캐스팅 감독 (Casting Director)",
            }
        }
    }
