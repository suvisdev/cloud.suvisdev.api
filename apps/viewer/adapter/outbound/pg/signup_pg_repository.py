from __future__ import annotations

import hashlib
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.matrix.oracle_database import get_secom_session_factory
from viewer.app.dtos.auth_command_dto import SignupCommand
from viewer.app.dtos.user_model import User, resolve_user_group_id
from viewer.app.dtos.user_profile import UserAgeGroup, UserGender
from viewer.app.ports.output.signup_repository import SignupRepository

logger = logging.getLogger(__name__)


def _hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


class SignupPgRepository(SignupRepository):
    """viewer 회원가입 PostgreSQL 아웃바운드 어댑터."""

    async def save_user(self, command: SignupCommand) -> int:
        user_payload = command.user
        username = user_payload.username
        logger.info("[SignupPgRepository] save_user 진입 — username=%s", username)

        user_group_id = await resolve_user_group_id()
        factory = get_secom_session_factory()
        async with factory() as session:
            existing = await session.execute(
                select(User.id).where(User.username == username),
            )
            if existing.scalar_one_or_none() is not None:
                raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")

            user = User(
                group_id=user_group_id,
                username=username,
                password_hash=_hash_password(user_payload.password),
                nickname=user_payload.nickname,
                email=user_payload.email,
                gender=user_payload.gender or UserGender.UNDISCLOSED,
                age_group=user_payload.age_group or UserAgeGroup.UNDISCLOSED,
                birth_year=user_payload.birth_year,
                preferred_genres=list(user_payload.preferred_genres or []),
                bio=(user_payload.bio or "").strip(),
            )
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError as exc:
                await session.rollback()
                raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.") from exc
            user_id = user.id

        logger.info("[SignupPgRepository] save_user 완료 — user_id=%s", user_id)
        return user_id
