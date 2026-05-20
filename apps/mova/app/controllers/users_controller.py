import logging

from mova.app.schemas.users_schema import (
    MovaUserCreateSchema,
    MovaUserSchema,
    MovaUserUpdateSchema,
)
from mova.app.services.users_service import UsersService

logger = logging.getLogger(__name__)


class UsersController:
    def __init__(self) -> None:
        self.users_service = UsersService()

    async def save_user(self, payload: MovaUserCreateSchema) -> MovaUserSchema:
        logger.info("[UsersController] save_user — %s", payload.email)
        return await self.users_service.save_user(payload)

    async def update_user(
        self,
        user_id: int,
        payload: MovaUserUpdateSchema,
    ) -> MovaUserSchema:
        logger.info("[UsersController] update_user — id=%s", user_id)
        return await self.users_service.update_user(user_id, payload)

    async def get_user(self, user_id: int) -> MovaUserSchema:
        return await self.users_service.get_user(user_id)

    async def get_user_by_email(self, email: str) -> MovaUserSchema:
        return await self.users_service.get_user_by_email(email)

    async def list_users(self, limit: int = 100) -> list[MovaUserSchema]:
        return await self.users_service.list_users(limit=limit)
