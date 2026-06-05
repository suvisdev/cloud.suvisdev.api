from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LoginUserCommand:
    username: str
    password: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> LoginUserCommand:
        return cls(
            username=str(payload.get("username", "")),
            password=str(payload.get("password", "")),
        )

    def to_payload(self) -> dict[str, Any]:
        return {"username": self.username, "password": self.password}


@dataclass
class SignupUserCommand:
    username: str
    password: str
    nickname: str
    email: str
    gender: str
    age_group: str
    birth_year: int | None
    preferred_genres: list[str] | None
    bio: str | None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SignupUserCommand:
        member = payload.get("member") if isinstance(payload.get("member"), dict) else {}
        return cls(
            username=str(payload.get("username", "")),
            password=str(payload.get("password", "")),
            nickname=str(payload.get("nickname", "")),
            email=str(payload.get("email", "")),
            gender=str(member.get("gender", payload.get("gender", "undisclosed"))),
            age_group=str(member.get("age_group", payload.get("age_group", "undisclosed"))),
            birth_year=member.get("birth_year", payload.get("birth_year")),
            preferred_genres=member.get("preferred_genres", payload.get("preferred_genres")),
            bio=member.get("bio", payload.get("bio")),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password,
            "nickname": self.nickname,
            "email": self.email,
            "gender": self.gender,
            "age_group": self.age_group,
            "birth_year": self.birth_year,
            "preferred_genres": self.preferred_genres,
            "bio": self.bio,
        }


@dataclass
class SignupCommand:
    user: SignupUserCommand

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SignupCommand:
        user_payload = dict(payload.get("user", payload))
        if isinstance(payload.get("member"), dict):
            user_payload["member"] = payload["member"]
        return cls(user=SignupUserCommand.from_payload(user_payload))

    def to_payload(self) -> dict[str, Any]:
        return {"user": self.user.to_payload()}
