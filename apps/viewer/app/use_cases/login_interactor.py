from __future__ import annotations

import logging

from viewer.adapter.inbound.api.schemas.login_schema import LoginSchema
from viewer.app.dtos.auth_command_dto import LoginResponseDto, LoginUserCommand
from viewer.app.ports.input.login_use_case import LoginUseCase
from viewer.app.ports.output.login_repository import LoginRepository

logger = logging.getLogger(__name__)


class LoginInteractor(LoginUseCase):
    """login_router → 입력 포트 → 출력 포트(repository) → DB."""

    def __init__(self, repository: LoginRepository) -> None:
        self._repository = repository

    async def login(self, payload: LoginSchema) -> LoginResponseDto:
        logger.info("🤖 [LoginInteractor] login 진입")
        command = LoginUserCommand.from_schema(payload)
        user_id = await self._repository.login_user(command)
        logger.info("🤖 [LoginInteractor] login 완료 — user_id=%s", user_id)
        return LoginResponseDto(user_id=user_id)
