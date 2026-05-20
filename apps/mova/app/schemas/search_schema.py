from typing import Literal

from pydantic import BaseModel, Field

MatchType = Literal["title", "person", "keyword", "synopsis"]


class MovaSearchItemSchema(BaseModel):
    """프론트 `MovaSearchResult` 와 동일한 필드."""

    id: str = Field(..., description="영화 slug (`/mova/title/{id}`)")
    title: str
    year: str
    rating: float
    poster: str
    match_type: MatchType
