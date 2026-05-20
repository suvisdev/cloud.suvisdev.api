from pydantic import BaseModel, Field


class MovieImportResultSchema(BaseModel):
    imported: int = Field(description="신규·갱신된 영화 수")
    movie_ids: list[int] = Field(default_factory=list)
    rankings_updated: bool = False
    message: str = ""
