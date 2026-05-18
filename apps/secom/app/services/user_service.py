import logging

from secom.app.repositories.user_repository import UserRepository
from secom.app.schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)
_LAYER = "UserService"


class UserService:
    def __init__(self) -> None:
        pass

    def save_user(self, user_schema: UserSchema) -> None:
        payload = user_schema.model_dump()
        logger.info("[%s] save_user 진입 — values=%s", _LAYER, payload)

        user_repository = UserRepository()
        user_repository.save_user(user_schema)

        logger.info("[%s] save_user 완료 — username=%s", _LAYER, payload.get("username"))
