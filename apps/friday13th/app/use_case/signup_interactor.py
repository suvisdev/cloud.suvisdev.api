from __future__ import annotations

from typing import Any

from friday13th.app.ports.input.signup_use_case import SignupUseCase
from friday13th.app.ports.output.signup_repository import SignupRepository

class SignupInteractor(SignupUseCase):
    """signup_router → 입력 포트 → 출력 포트(repository) → DB."""

    def __init__(self, repository: SignupRepository | None = None) -> None:
        self._repository = repository

    async def signup(self, payload: dict[str, Any]) -> int:
        return await self._repository.save_user(payload)
