from pydantic import BaseModel, Field


class TagCreateSchema(BaseModel):
    movie_id: int = Field(..., gt=0)
    label: str = Field(..., min_length=1, max_length=255, description="표시 라벨")
    slug: str | None = Field(default=None, max_length=64)
    description: str = Field(default="", description="태그 설명(선택)")
    character_id: int | None = Field(
        default=None,
        gt=0,
        description="cast 태그용 characters.id (영화–인물 연결)",
    )
    tag_kind: str = Field(default="mood", description="mood | genre | cast")


class TagSchema(BaseModel):
    id: int
    movie_id: int
    character_id: int | None = None
    tag_kind: str = "mood"
    slug: str
    label: str
    description: str = ""


class TagCatalogSchema(BaseModel):
    """slug 기준 distinct 카탈로그 (채팅 버튼 등)."""

    slug: str
    label: str
    description: str = ""


class MoviesByTagSchema(BaseModel):
    tag_id: int
    movie_id: int
    slug: str
    tag_slug: str
    tag_label: str
    title: str
    release_year: str
    poster: str
