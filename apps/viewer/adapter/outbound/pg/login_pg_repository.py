from __future__ import annotations

import hashlib
import logging

from fastapi import HTTPException
from sqlalchemy import select

from core.matrix.oracle_database import get_secom_session_factory
from viewer.app.dtos.admin_model import Admin
from viewer.app.dtos.auth_command_dto import LoginUserCommand
from viewer.app.dtos.user_model import User
from viewer.app.ports.output.login_repository import LoginRepository

logger = logging.getLogger(__name__)


def _verify_password(raw_password: str, stored_password_hash: str) -> bool:
    digest = hashlib.sha256(raw_password.encode("utf-8")).hexdigest()
    return stored_password_hash == raw_password or stored_password_hash == digest


class LoginPgRepository(LoginRepository):
    """Viewer 로그인 PostgreSQL 아웃바운드 어댑터 — users 우선, 없으면 admins."""

    async def login_user(self, command: LoginUserCommand) -> int:
        username = command.username
        password = command.password
        logger.info("[LoginPgRepository] login_user 진입 — username=%s", username)

        factory = get_secom_session_factory()
        async with factory() as session:
            user = (
                await session.execute(select(User).where(User.username == username))
            ).scalar_one_or_none()
            if user is not None and _verify_password(password, user.password_hash):
                logger.info("[LoginPgRepository] login_user 완료 — user_id=%s", user.id)
                return user.id

            admin = (
                await session.execute(select(Admin).where(Admin.username == username))
            ).scalar_one_or_none()
            if admin is not None and _verify_password(password, admin.password_hash):
                logger.info("[LoginPgRepository] login_user 완료 — admin_id=%s", admin.id)
                return admin.id

            raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
