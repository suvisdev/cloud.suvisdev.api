import logging

from friday13th.app.schemas.auth_schema import LoginSchema, UserSchema
from friday13th.app.services.user_service import UserService

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self) -> None:
        self.user_service = UserService()

    async def save_user(self, user_schema: UserSchema) -> int:
        logger.info("[UserController] save_user 진입 — %s", user_schema.log_summary())
        return await self.user_service.save_user(user_schema)

    async def login_user(self, login_schema: LoginSchema) -> int:
        logger.info("[UserController] login_user 진입 — %s", login_schema.log_summary())
        return await self.user_service.login_user(login_schema)
