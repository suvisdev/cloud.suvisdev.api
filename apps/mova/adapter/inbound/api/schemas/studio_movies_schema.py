from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MovieCreateSchema(BaseModel):
    title: str
    slug: str | None = None
    release_year: str = ""
    rating: float = 0.0
    poster: str = ""
    platform: Literal["netflix", "disney"] | None = None
    genres: list[str] = Field(default_factory=list)


class MovieTitleCreateSchema(BaseModel):
    title: str


class StudioMoviesSchema(BaseModel):

    id: int = Field(0, description="Movies ID")
    name: str = Field("감독 (Director)", description="Director's name")
    # 영화를 완성하고 지휘하는 연출자. movies 테이블의 핵심 엔티티

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "감독 (Director)",
            }
        }
    }
