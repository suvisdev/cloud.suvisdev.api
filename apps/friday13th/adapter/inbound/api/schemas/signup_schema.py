from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class SignupUserSchema(BaseModel):
    """USERS 기반 회원가입 스키마."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=128)
    nickname: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="user", max_length=16)


class SignupMemberSchema(BaseModel):
    """MEMBERS 기반 회원 프로필 스키마."""

    gender: str = Field(default="undisclosed", max_length=32)
    age_group: str = Field(default="undisclosed", max_length=32)
    birth_year: int | None = None
    preferred_genres: list[str] | None = None
    bio: str | None = None


class SignupSchema(BaseModel):
    """회원가입 요청: USERS + MEMBERS 조합."""

    user: SignupUserSchema
    member: SignupMemberSchema = Field(default_factory=SignupMemberSchema)

    @model_validator(mode="before")
    @classmethod
    def _accept_flat_payload(cls, values: Any) -> Any:
        if not isinstance(values, dict):
            return values
        if "user" in values or "member" in values:
            return values
        return {
            "user": {
                "username": values.get("username"),
                "password": values.get("password"),
                "nickname": values.get("nickname"),
                "email": values.get("email"),
                "role": values.get("role", "user"),
            },
            "member": {
                "gender": values.get("gender", "undisclosed"),
                "age_group": values.get("age_group", "undisclosed"),
                "birth_year": values.get("birth_year"),
                "preferred_genres": values.get("preferred_genres"),
                "bio": values.get("bio"),
            },
        }

    def log_summary(self) -> dict[str, str]:
        return {"username": self.user.username}
