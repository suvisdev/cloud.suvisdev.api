from __future__ import annotations

from pydantic import BaseModel, Field


class MovaSearchItemSchema(BaseModel):
    id: str
    title: str
    year: str
    rating: float
    poster: str
    match_type: str


class StudioSearchSchema(BaseModel):

    id: int = Field(0, description="Search ID")
    name: str = Field("검색 감독 (Search Director)", description="Search Director's name")
    # 키워드·벡터 검색으로 영화를 찾아주는 검색 담당자

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "검색 감독 (Search Director)",
            }
        }
    }
