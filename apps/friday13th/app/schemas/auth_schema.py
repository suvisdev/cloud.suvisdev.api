from pydantic import BaseModel, Field

from friday13th.app.models.role import UserRole


class CredentialsSchema(BaseModel):
    """로그인·회원가입 공통 필드."""

    username: str
    password: str


class LoginSchema(CredentialsSchema):
    """로그인 요청."""

    def log_summary(self) -> str:
        return f"아이디={self.username} | 비밀번호=****"


class UserSchema(CredentialsSchema):
    """회원가입 요청."""

    nickname: str
    email: str
    role: str = Field(default=UserRole.USER)
    gender: str | None = Field(default=None, description="male|female|other|undisclosed")
    age_group: str | None = Field(
        default=None,
        description="10s|20s|30s|40s|50s|60s_plus|undisclosed",
    )
    birth_year: int | None = Field(default=None, ge=1900, le=2100)
    preferred_genres: list[str] = Field(default_factory=list)
    bio: str = Field(default="", max_length=255)

    def log_summary(self) -> str:
        return (
            f"아이디={self.username} | 비밀번호=**** | "
            f"닉네임={self.nickname} | 이메일={self.email} | 역할={self.role} | "
            f"성별={self.gender} | 연령대={self.age_group}"
        )
