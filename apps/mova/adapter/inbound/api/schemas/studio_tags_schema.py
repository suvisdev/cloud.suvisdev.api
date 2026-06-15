from __future__ import annotations

from pydantic import BaseModel, Field


class TagCreateSchema(BaseModel):
    movie_id: int
    label: str
    slug: str = ""
    description: str = ""
    character_id: int | None = None
    tag_kind: str = "mood"


class TagSchema(BaseModel):
    id: int
    movie_id: int
    character_id: int | None
    tag_kind: str
    slug: str
    label: str
    description: str


class TagCatalogSchema(BaseModel):
    slug: str
    label: str
    description: str


class MoviesByTagSchema(BaseModel):
    tag_id: int
    movie_id: int
    slug: str
    tag_slug: str
    tag_label: str
    title: str
    release_year: str
    poster: str


class StudioTagsSchema(BaseModel):

    id: int = Field(0, description="Tags ID")
    name: str = Field("홍보 담당자 (Publicist)", description="Publicist's name")
    # 영화의 분위기·장르·인물을 대중 언어로 표현하는 홍보 전문가. tags 테이블 관리

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "홍보 담당자 (Publicist)",
            }
        }
    }
