from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.walter_dto import WalterPassengerPage


class WalterUseCase(ABC):
    """승객 목록 조회(GET) 입력 포트 (ABC).

    API·라우터가 호출하는 화면 단위 조회만 정의한다.
    DB 목록/건수 읽기는 출력 포트 WalterReader.read_passengers_page 에 맡기고,
    WalterInteractor 가 두 포트 사이를 연결한다.
    """

    @abstractmethod
    async def get_passenger_page(page: int, page_size: int) -> WalterPassengerPage:
        pass
