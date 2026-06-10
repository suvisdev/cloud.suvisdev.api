from fastapi import APIRouter, Depends
from titanic.adapter.inbound.api.schemas.crew_smith_captain_schema import SmithCaptainSchema
from titanic.app.ports.input.crew_smith_captain_use_case import SmithCaptainUseCase
from titanic.dependencies.crew_smith_captain_provider import get_smith_captain_use_case
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse

smith_captain_router = APIRouter(prefix="/smith", tags=["smith"])


@smith_captain_router.post("/chat")
async def chat(
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case),
) -> SmithCaptainResponse:
    return None


@smith_captain_router.get("/myself")
async def introduce_myself(
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case),
) -> SmithCaptainResponse:
    return await smith.introduce_myself(
        SmithCaptainSchema(
            id=4,
            name="스미스 캡틴 주인공"
        )
    )
