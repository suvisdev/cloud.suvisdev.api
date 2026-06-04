from __future__ import annotations

from abc import ABC, abstractmethod

from mova.adapter.inbound.api.schemas.search_schema import MovaSearchItemSchema


class SearchUseCase(ABC):
    """검색(search) 입력 포트."""

    @abstractmethod
    async def search(self, query: str, *, limit: int = 12) -> list[MovaSearchItemSchema]:
        pass
