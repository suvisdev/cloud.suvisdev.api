import logging

from mova.app.repositories.users_repository import UsersRepository, UsersRepositoryError
from mova.app.schemas.users_schema import (
    MovaUserCreateSchema,
    MovaUserSchema,
    MovaUserUpdateSchema,
)

logger = logging.getLogger(__name__)


class UsersService:
    """Mova 취향 분석용 사용자 (`users`)."""

    def __init__(self) -> None:
        self.users_repository = UsersRepository()

    def _to_schema(self, row) -> MovaUserSchema:
        return MovaUserSchema(
            id=row.id,
            nickname=row.nickname,
            email=row.email,
            preferred_genres=list(row.preferred_genres or []),
        )

    async def save_user(self, payload: MovaUserCreateSchema) -> MovaUserSchema:
        logger.info("[UsersService] save_user — %s", payload.email)
        row = await self.users_repository.upsert(
            {
                "nickname": payload.nickname,
                "email": str(payload.email),
                "preferred_genres": payload.preferred_genres,
            },
        )
        return self._to_schema(row)

    async def update_user(
        self,
        user_id: int,
        payload: MovaUserUpdateSchema,
    ) -> MovaUserSchema:
        logger.info("[UsersService] update_user — id=%s", user_id)
        row = await self.users_repository.update(
            user_id,
            {
                "nickname": payload.nickname,
                "preferred_genres": payload.preferred_genres,
            },
        )
        return self._to_schema(row)

    async def get_user(self, user_id: int) -> MovaUserSchema:
        row = await self.users_repository.get_by_id(user_id)
        if row is None:
            raise UsersRepositoryError(
                f"사용자 ID {user_id}를 찾을 수 없습니다.",
                status_code=404,
            )
        return self._to_schema(row)

    async def get_user_by_email(self, email: str) -> MovaUserSchema:
        row = await self.users_repository.get_by_email(email)
        if row is None:
            raise UsersRepositoryError(
                "해당 이메일의 사용자를 찾을 수 없습니다.",
                status_code=404,
            )
        return self._to_schema(row)

    async def list_users(self, limit: int = 100) -> list[MovaUserSchema]:
        rows = await self.users_repository.list_users(limit=limit)
        return [self._to_schema(r) for r in rows]
