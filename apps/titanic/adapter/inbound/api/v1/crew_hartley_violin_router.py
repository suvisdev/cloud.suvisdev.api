from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.dependencies.crew_hartley_violin import get_crew_hartley_violin_use_case

crew_hartley_violin_router = APIRouter(prefix="/titanic/violin", tags=["violin"])


@crew_hartley_violin_router.get("/violin", response_model=int)
async def get_violin(
    use_case: HartleyViolinUseCase = Depends(get_crew_hartley_violin_use_case),
) -> int:
    return await use_case.get_violin({})
