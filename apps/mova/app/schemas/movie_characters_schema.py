from pydantic import BaseModel, Field


class MovieCharacterLinkCreateSchema(BaseModel):
    movie_id: int = Field(..., gt=0, description="영화 ID (`movies.id`)")
    actor_id: int = Field(..., gt=0, description="인물 ID (`actors.id`)")


class MovieCharacterLinkSchema(BaseModel):
    id: int
    movie_id: int
    actor_id: int


class MovieCharacterWithActorSchema(BaseModel):
    id: int
    movie_id: int
    actor_id: int
    actor_name: str
    role_type: str
    profile_photo: str


class MovieCharacterWithMovieSchema(BaseModel):
    id: int
    movie_id: int
    actor_id: int
    slug: str
    movie_title: str
    release_year: str
    rating: float
    poster: str
    platform: str | None = None
