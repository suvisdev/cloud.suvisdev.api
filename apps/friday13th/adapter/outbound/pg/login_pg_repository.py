from __future__ import annotations

from sqlalchemy import select

from core.database import get_secom_session_factory
from friday13th.app.dtos.user_model import User
from friday13th.app.ports.output.login_repository import LoginRepository

class LoginPgRepository(LoginRepository):
    """Friday13th 로그인 PostgreSQL 아웃바운드 어댑터."""

    async def login_user(self, payload: dict[str, Any]) -> int:
        factory = get_secom_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(User).where(User.username == payload["username"]),
            )
            user = result.scalar_one_or_none()
            if user is None or not verify_password(payload["password"], user.password_hash):
                raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
            return user.id
