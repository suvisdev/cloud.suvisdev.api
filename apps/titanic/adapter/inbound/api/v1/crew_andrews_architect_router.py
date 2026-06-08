from __future__ import annotations

from fastapi import APIRouter, Depends

from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsBlueprintUseCase
from titanic.dependencies.crew_andrews_architect import get_crew_andrews_architect_use_case

crew_andrews_architect_router = APIRouter(prefix="/titanic/andrews", tags=["andrews"])


@crew_andrews_architect_router.get("/blueprint", response_model=int)
async def get_blueprint(
    use_case: AndrewsBlueprintUseCase = Depends(get_crew_andrews_architect_use_case),
) -> int:
    return await use_case.get_blueprint({})
