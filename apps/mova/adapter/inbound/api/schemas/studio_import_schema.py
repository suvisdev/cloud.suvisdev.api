from __future__ import annotations

from pydantic import BaseModel, Field


class MovieImportResultSchema(BaseModel):
    imported: int
    movie_ids: list[int] = Field(default_factory=list)
    rankings_updated: bool = False
    message: str = ""


class TmdbImportRequestSchema(BaseModel):
    tmdb_id: int | None = Field(None, description="TMDB movie id")
    query: str | None = Field(None, description="제목 검색어")
    popular_pages: int = Field(
        0,
        ge=0,
        le=5,
        description="popular 목록 페이지 수 (tmdb_id·query 없을 때)",
    )


class StudioImportSchema(BaseModel):
    id: int = Field(0, description="Import ID")
    name: str = Field("수입 감독 (Import Director)", description="Import Director's name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "수입 감독 (Import Director)",
            }
        }
    }
