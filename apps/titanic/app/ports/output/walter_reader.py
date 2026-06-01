from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.walter_dto import WalterPassengerItem


class WalterReader(ABC):
    """승객 목록 조회 아웃바운드 포트 (ABC).

    DB에서 (목록, 전체 건수)를 한 번에 읽는다.
    페이지 번호·total_pages 계산은 입력 포트(WalterUseCase)를 구현하는 WalterInteractor가 담당한다.
    """

    @abstractmethod
    async def read_passengers_page(
        offset: int,
        limit: int,
    ) -> tuple[list[WalterPassengerItem], int]:
        pass
