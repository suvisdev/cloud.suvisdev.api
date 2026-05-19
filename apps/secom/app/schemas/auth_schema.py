from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    """로그인·회원가입 공통 필드."""

    username: str
    password: str


class LoginSchema(CredentialsSchema):
    """로그인 요청."""

    def log_summary(self) -> str:
        return f"아이디={self.username} | 비밀번호={self.password}"


class UserSchema(CredentialsSchema):
    """회원가입 요청."""

    nickname: str
    email: str
    role: str = Field(default="user")

    def log_summary(self) -> str:
        return (
            f"아이디={self.username} | 비밀번호={self.password} | "
            f"닉네임={self.nickname} | 이메일={self.email}"
        )
