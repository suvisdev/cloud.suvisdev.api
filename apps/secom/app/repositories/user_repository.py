import logging

from secom.app.schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)
_LAYER = "UserRepository"


class UserRepository:
    def __init__(self) -> None:
        pass

    def save_user(self, user_schema: UserSchema) -> None:
        payload = user_schema.model_dump()
        logger.info("[%s] save_user 진입 — values=%s", _LAYER, payload)

        # TODO: DB 저장 로직 연결
        logger.info(
            "[%s] save_user 처리 — username=%s, nickname=%s, email=%s, role=%s",
            _LAYER,
            payload.get("username"),
            payload.get("nickname"),
            payload.get("email"),
            payload.get("role"),
        )

        logger.info("[%s] save_user 완료 — username=%s", _LAYER, payload.get("username"))
