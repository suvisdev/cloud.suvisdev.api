from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from mova.adapter.inbound.api.schemas.chat_schema import MovaChatRequest, MovaChatResponseSchema
from mova.app.ports.input.chat_use_case import ChatUseCase
from mova.app.use_cases.chat_interactor import ChatInteractor

chat_router = APIRouter(tags=["mova-chat"])

logger = logging.getLogger(__name__)


@chat_router.post("/chat", response_model=MovaChatResponseSchema)
async def mova_chat(req: MovaChatRequest) -> MovaChatResponseSchema:
    """Mova AI 영화 추천 채팅."""
    logger.info("[ChatRouter] chat — message_len=%s", len(req.message))
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message가 비어 있습니다.")
    history = [{"role": h.role, "content": h.content} for h in req.history]
    use_case: ChatUseCase = ChatInteractor()
    try:
        return await use_case.chat(
            message,
            history,
            user_id=req.user_id,
            model_key=req.model,
        )
    except HTTPException:
        raise
    except RuntimeError as e:
        if "GEMINI" in str(e).upper() or "API_KEY" in str(e).upper():
            raise HTTPException(status_code=503, detail=str(e)) from e
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.exception("[ChatRouter] chat 실패")
        raise HTTPException(
            status_code=502,
            detail="추천 응답을 만들지 못했습니다. 잠시 후 다시 시도하세요.",
        ) from e
