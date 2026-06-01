from __future__ import annotations

from fastapi import APIRouter
from typing import Any

from friday13th.app.ports.input.login_use_case import LoginUseCase

login_router = APIRouter(prefix="/friday13th", tags=["login"])


@login_router.post("/login", response_model=int)
async def login(request: dict[str, Any]) -> int:
    login_use_case = LoginUseCase()
    return await login_use_case.login(request)

