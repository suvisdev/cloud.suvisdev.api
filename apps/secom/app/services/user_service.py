import logging

from secom.app.repositories.user_repository import UserRepository
from secom.app.schemas.auth_schema import LoginSchema, UserSchema

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()

    async def save_user(self, user_schema: UserSchema) -> None:
        logger.info("[UserService] save_user 진입 — %s", user_schema.log_summary())
        await self.user_repository.save_user(user_schema)

    async def login_user(self, login_schema: LoginSchema) -> None:
        logger.info("[UserService] login_user 진입 — %s", login_schema.log_summary())
        await self.user_repository.login_user(login_schema)
