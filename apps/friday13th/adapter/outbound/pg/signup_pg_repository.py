from __future__ import annotations

import hashlib
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.matrix.oracle_database import get_secom_session_factory
from friday13th.app.dtos.auth_command_dto import SignupCommand
from friday13th.app.dtos.role import UserRole
from friday13th.app.dtos.user_model import User
from friday13th.app.ports.output.signup_repository import SignupRepository

logger = logging.getLogger(__name__)


def _hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

class SignupPgRepository(SignupRepository):
    """Friday13th 회원가입 PostgreSQL 아웃바운드 어댑터."""

    async def save_user(self, command: SignupCommand) -> int:
        user_payload = command.user
        member_payload = command.member
        role = str(user_payload.role or UserRole.USER)
        username = user_payload.username
        # 🎁로그 코드 시작
        logger.info("🤖 [SignupPgRepository] save_user 진입 — username=%s", username)
        # 🎁로그 코드 끝

        factory = get_secom_session_factory()
        async with factory() as session:
            existing = await session.execute(
                select(User.id).where(User.username == username),
            )
            if existing.scalar_one_or_none() is not None:
                raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")

            user = User(
                role=role,
                username=username,
                password_hash=_hash_password(user_payload.password),
                nickname=user_payload.nickname,
                email=user_payload.email,
            )
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError as exc:
                await session.rollback()
                raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.") from exc
            user_id = user.id

        try:
            from friday13th.app.dtos.member_model import MemberRepository

            await MemberRepository().create_for_user(
                user_id,
                gender=member_payload.gender,
                age_group=member_payload.age_group,
                birth_year=member_payload.birth_year,
                preferred_genres=member_payload.preferred_genres,
                bio=member_payload.bio,
                user_role=role,
            )
        except Exception:
            logger.exception(
                "🤖 [SignupPgRepository] members 프로필 생성 실패 user_id=%s",
                user_id,
            )

        # 🎁로그 코드 시작
        logger.info("🤖 [SignupPgRepository] save_user 완료 — user_id=%s", user_id)
        # 🎁로그 코드 끝
        return user_id
