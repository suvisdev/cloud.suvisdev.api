from pydantic import BaseModel, Field


class TagCreateSchema(BaseModel):
    label: str = Field(..., min_length=1, max_length=255, description="감성 문구")
    slug: str | None = Field(default=None, max_length=64)
    description: str = Field(default="", description="태그 설명(선택)")


class TagSchema(BaseModel):
    id: int
    slug: str
    label: str
    description: str = ""


class MovieTagLinkCreateSchema(BaseModel):
    movie_id: int = Field(..., gt=0)
    tag_id: int = Field(..., gt=0)


class MovieTagLinkSchema(BaseModel):
    id: int
    movie_id: int
    tag_id: int


class MovieWithTagSchema(BaseModel):
    link_id: int
    movie_id: int
    tag_id: int
    slug: str
    title: str
    release_year: str
    poster: str


class TagWithMovieSchema(BaseModel):
    link_id: int
    movie_id: int
    tag_id: int
    tag_slug: str
    tag_label: str
