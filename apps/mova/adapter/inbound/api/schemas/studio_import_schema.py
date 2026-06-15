from __future__ import annotations

from pydantic import BaseModel, Field


class MovieImportResultSchema(BaseModel):
    imported: int
    movie_ids: list[int] = Field(default_factory=list)
    rankings_updated: bool = False
    message: str = ""


class StudioImportSchema(BaseModel):

    id: int = Field(0, description="Import ID")
    name: str = Field("수입 감독 (Import Director)", description="Import Director's name")
    # TMDB·KOFIC 외부 API 경유 영화 수입 담당자

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "수입 감독 (Import Director)",
            }
        }
    }
