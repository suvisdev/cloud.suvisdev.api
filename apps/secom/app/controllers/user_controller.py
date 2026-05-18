import logging

from secom.app.schemas.user_schema import UserSchema
from secom.app.services.user_service import UserService

logger = logging.getLogger(__name__)
_LAYER = "UserController"


class UserController:
    def __init__(self) -> None:
        pass

    def save_user(self, user_schema: UserSchema) -> None:
        payload = user_schema.model_dump()
        logger.info("[%s] save_user 진입 — values=%s", _LAYER, payload)

        user_service = UserService()
        user_service.save_user(user_schema)

        logger.info("[%s] save_user 완료 — username=%s", _LAYER, payload.get("username"))
