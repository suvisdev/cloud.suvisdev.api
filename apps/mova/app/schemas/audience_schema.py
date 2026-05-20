from pydantic import BaseModel, Field


class MovaChatRecommendationSchema(BaseModel):
    id: str
    title: str
    year: str
    poster: str
    synopsis: str
    platform: str | None = None
    hook: str = Field(description="한 줄 추천 이유")


class MovaChatResponseSchema(BaseModel):
    reply: str
    recommendations: list[MovaChatRecommendationSchema] = Field(default_factory=list)
    refined_query: str | None = None
    keywords: list[str] = Field(default_factory=list)
