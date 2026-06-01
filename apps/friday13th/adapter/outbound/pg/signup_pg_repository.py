from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.database import get_secom_session_factory
from friday13th.app.auth_errors import UserRepositoryError
from friday13th.app.dtos.role import UserRole
from friday13th.app.dtos.user_model import User
from friday13th.app.ports.output.signup_repository import SignupRepository
from friday13th.app.schemas.auth_schema import UserSchema
from friday13th.app.security import hash_password

class SignupPgRepository(SignupRepository):
    """Friday13th 회원가입 PostgreSQL 아웃바운드 어댑터."""

    async def save_user(self, payload: dict[str, Any]) -> int:
        factory = get_secom_session_factory()
        async with factory() as session:
            existing = await session.execute(
                select(User.id).where(User.username == payload["username"]),
            )
            if existing.scalar_one_or_none() is not None:
                raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")

            user = User(
                role=role,
                username=payload["username"],
                password_hash=hash_password(payload["password"]),
                nickname=payload["nickname"],
                email=payload["email"],
            )
            session.add(user)
            try:
                await session.commit()
                await session.refresh(user)
            except IntegrityError as exc:
                await session.rollback()
                raise UserRepositoryError("이미 사용 중인 아이디입니다.", status_code=409) from exc
            user_id = user.id

        try:
            from friday13th.app.dtos.member_model import MemberRepository

            await MemberRepository().create_for_user(
                user_id,
                gender=user_schema.gender,
                age_group=user_schema.age_group,
                birth_year=user_schema.birth_year,
                preferred_genres=user_schema.preferred_genres,
                bio=user_schema.bio,
                user_role=role,
            )
        except Exception:
            logger.exception(
                "🤖 [SignupPgRepository] members 프로필 생성 실패 user_id=%s",
                user_id,
            )

        logger.info("🤖 [SignupPgRepository] save_user 완료 — user_id=%s", user_id)
        return user_id
