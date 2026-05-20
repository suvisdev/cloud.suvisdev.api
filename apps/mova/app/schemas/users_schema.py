from pydantic import BaseModel, Field


class MovaUserCreateSchema(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=3, max_length=255, description="이메일")
    preferred_genres: list[str] = Field(
        default_factory=list,
        description="선호 장르 (예: SF, 드라마, 코미디)",
    )


class MovaUserUpdateSchema(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=50)
    preferred_genres: list[str] | None = Field(default=None)


class MovaUserSchema(BaseModel):
    id: int
    nickname: str
    email: str
    preferred_genres: list[str] = Field(default_factory=list)
