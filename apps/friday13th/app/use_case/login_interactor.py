from __future__ import annotations

import logging

from friday13th.adapter.inbound.api.schemas.login_schema import LoginSchema
from friday13th.app.dtos.auth_command_dto import LoginUserCommand
from friday13th.app.ports.input.login_use_case import LoginUseCase
from friday13th.app.ports.output.login_repository import LoginRepository

logger = logging.getLogger(__name__)


class LoginInteractor(LoginUseCase):
    """login_router → 입력 포트 → 출력 포트(repository) → DB."""

    def __init__(self, repository: LoginRepository) -> None:
        self._repository = repository

    async def login(self, payload: LoginSchema) -> int:
        # 🎁로그 코드 시작
        logger.info("🤖 [LoginInteractor] login 진입")
        # 🎁로그 코드 끝
        command = LoginUserCommand.from_payload(payload.model_dump())
        user_id = await self._repository.login_user(command)
        # 🎁로그 코드 시작
        logger.info("🤖 [LoginInteractor] login 완료 — user_id=%s", user_id)
        # 🎁로그 코드 끝
        return user_id
