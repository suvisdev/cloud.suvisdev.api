from __future__ import annotations

import hashlib
import logging

from fastapi import HTTPException
from sqlalchemy import select

from core.matrix.oracle_database import get_secom_session_factory
from friday13th.app.dtos.auth_command_dto import LoginUserCommand
from friday13th.app.dtos.user_model import User
from friday13th.app.ports.output.login_repository import LoginRepository

logger = logging.getLogger(__name__)


def _verify_password(raw_password: str, stored_password_hash: str) -> bool:
    # Support both legacy plain-text rows and hashed rows.
    digest = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
    return stored_password_hash == raw_password or stored_password_hash == digest


class LoginPgRepository(LoginRepository):
    """Friday13th 로그인 PostgreSQL 아웃바운드 어댑터."""

    async def login_user(self, command: LoginUserCommand) -> int:
        username = command.username
        password = command.password
        # 🎁로그 코드 시작
        logger.info("🤖 [LoginPgRepository] login_user 진입 — username=%s", username)
        # 🎁로그 코드 끝
        factory = get_secom_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(User).where(User.username == username),
            )
            user = result.scalar_one_or_none()
            if user is None or not _verify_password(password, user.password_hash):
                raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
            # 🎁로그 코드 시작
            logger.info("🤖 [LoginPgRepository] login_user 완료 — user_id=%s", user.id)
            # 🎁로그 코드 끝
            return user.id
