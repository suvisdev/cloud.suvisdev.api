import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import get_session_factory
from mova.app.models.users_model import MovaUser

logger = logging.getLogger(__name__)


class UsersRepositoryError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UsersRepository:
    async def get_by_id(self, user_id: int) -> MovaUser | None:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaUser).where(MovaUser.id == user_id))
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> MovaUser | None:
        normalized = email.strip().lower()
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaUser).where(MovaUser.email == normalized),
            )
            return result.scalar_one_or_none()

    async def upsert(self, data: dict) -> MovaUser:
        email = str(data.get("email", "")).strip().lower()
        nickname = str(data.get("nickname", "")).strip()
        if not email:
            raise UsersRepositoryError("이메일이 비어 있습니다.", status_code=400)
        if not nickname:
            raise UsersRepositoryError("닉네임이 비어 있습니다.", status_code=400)

        genres = list(data.get("preferred_genres") or [])

        logger.info("[UsersRepository] upsert — email=%r nickname=%r", email, nickname)
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaUser).where(MovaUser.email == email))
            row = result.scalar_one_or_none()
            if row is None:
                row = MovaUser(
                    email=email[:255],
                    nickname=nickname[:50],
                    preferred_genres=genres,
                )
                session.add(row)
            else:
                row.nickname = nickname[:50]
                if data.get("preferred_genres") is not None:
                    row.preferred_genres = genres

            try:
                await session.commit()
                await session.refresh(row)
            except IntegrityError as e:
                await session.rollback()
                raise UsersRepositoryError(
                    "사용자 저장에 실패했습니다.",
                    status_code=409,
                ) from e
            return row

    async def update(self, user_id: int, data: dict) -> MovaUser:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(select(MovaUser).where(MovaUser.id == user_id))
            row = result.scalar_one_or_none()
            if row is None:
                raise UsersRepositoryError(
                    f"사용자 ID {user_id}를 찾을 수 없습니다.",
                    status_code=404,
                )

            if data.get("nickname") is not None:
                nickname = str(data["nickname"]).strip()
                if not nickname:
                    raise UsersRepositoryError("닉네임이 비어 있습니다.", status_code=400)
                row.nickname = nickname[:50]
            if data.get("preferred_genres") is not None:
                row.preferred_genres = list(data["preferred_genres"])

            await session.commit()
            await session.refresh(row)
            return row

    async def list_users(self, limit: int = 100) -> list[MovaUser]:
        factory = get_session_factory()
        async with factory() as session:
            result = await session.execute(
                select(MovaUser).order_by(MovaUser.id.desc()).limit(limit),
            )
            return list(result.scalars().all())
