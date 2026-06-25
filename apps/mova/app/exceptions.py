"""LLM 호출 도메인 예외.

아웃바운드 LLM 어댑터는 FastAPI(HTTPException, 인바운드 관심사)에 의존하지 않는다.
대신 이 예외를 던지고, 인바운드 레이어가 단일 지점에서 HTTP 로 변환한다.
기존 도메인 예외 ``core.matrix.weather_reader.WeatherReaderError`` 와 동일하게
``status_code`` 를 실어 보내, 인바운드가 상태코드를 그대로 매핑하도록 한다.
"""

from __future__ import annotations


class LLMError(Exception):
    """LLM 호출 실패 기본 예외."""

    status_code = 503

    def __init__(self, detail: str, *, status_code: int | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class LLMTimeoutError(LLMError):
    """LLM 응답 타임아웃."""

    status_code = 504


class LLMUnavailableError(LLMError):
    """LLM 서비스 사용 불가 (API 키 미설정·모델 초기화 실패 등)."""

    status_code = 503
