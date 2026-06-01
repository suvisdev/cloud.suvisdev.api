from __future__ import annotations

from fastapi import APIRouter
from typing import Any

from friday13th.app.ports.input.signup_use_case import SignupUseCase

signup_router = APIRouter(prefix="/friday13th", tags=["signup"])

@signup_router.post("/signup", response_model=int)
async def signup(request: dict[str, Any]) -> int:
    signup_use_case = SignupUseCase()
    return await signup_use_case.signup(request)



