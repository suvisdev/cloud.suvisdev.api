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
    role: str

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SignupUserCommand:
        return cls(
            username=str(payload.get("username", "")),
            password=str(payload.get("password", "")),
            nickname=str(payload.get("nickname", "")),
            email=str(payload.get("email", "")),
            role=str(payload.get("role", "user")),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "password": self.password,
            "nickname": self.nickname,
            "email": self.email,
            "role": self.role,
        }


@dataclass
class SignupMemberCommand:
    gender: str
    age_group: str
    birth_year: int | None
    preferred_genres: list[str] | None
    bio: str | None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SignupMemberCommand:
        return cls(
            gender=str(payload.get("gender", "undisclosed")),
            age_group=str(payload.get("age_group", "undisclosed")),
            birth_year=payload.get("birth_year"),
            preferred_genres=payload.get("preferred_genres"),
            bio=payload.get("bio"),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "gender": self.gender,
            "age_group": self.age_group,
            "birth_year": self.birth_year,
            "preferred_genres": self.preferred_genres,
            "bio": self.bio,
        }


@dataclass
class SignupCommand:
    user: SignupUserCommand
    member: SignupMemberCommand

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> SignupCommand:
        user_payload = payload.get("user", payload)
        member_payload = payload.get("member", payload)
        return cls(
            user=SignupUserCommand.from_payload(user_payload),
            member=SignupMemberCommand.from_payload(member_payload),
        )

    def to_payload(self) -> dict[str, Any]:
        return {"user": self.user.to_payload(), "member": self.member.to_payload()}
