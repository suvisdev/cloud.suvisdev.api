from __future__ import annotations

from pydantic import BaseModel, Field

from friday13th.app.dtos.role import UserRole


class LoginSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)

    def log_summary(self) -> str:
        return f"username={self.username}"


class UserSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)
    nickname: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default=UserRole.USER, max_length=16)
    gender: str = Field(default="undisclosed", max_length=32)
    age_group: str = Field(default="undisclosed", max_length=32)
    birth_year: int | None = None
    preferred_genres: list[str] | None = None
    bio: str | None = None

    def log_summary(self) -> str:
        return f"username={self.username} email={self.email}"
