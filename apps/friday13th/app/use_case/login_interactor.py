from __future__ import annotations

from typing import Any

from friday13th.app.ports.input.login_use_case import LoginUseCase
from friday13th.app.ports.output.login_repository import LoginRepository


class LoginInteractor(LoginUseCase):
    """login_router → 입력 포트 → 출력 포트(repository) → DB."""

    def __init__(self, repository: LoginRepository | None = None) -> None:
        self._repository = repository

    async def login(self, payload: dict[str, Any]) -> int:
        return await self._repository.login_user(payload)
