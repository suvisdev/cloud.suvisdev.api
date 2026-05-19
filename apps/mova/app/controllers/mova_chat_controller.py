import logging

from mova.app.services.mova_chat_service import MovaChatService

logger = logging.getLogger(__name__)


class MovaChatController:
    def __init__(self) -> None:
        self.mova_chat_service = MovaChatService()

    async def build_prompt(self, history: list[dict[str, str]], message: str) -> str:
        logger.info("[MovaChatController] build_prompt 진입")
        catalog = await self.mova_chat_service.build_catalog_snippet()
        return self.mova_chat_service.build_prompt(catalog, history, message)
