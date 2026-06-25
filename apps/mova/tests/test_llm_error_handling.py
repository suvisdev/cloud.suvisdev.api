from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
APPS = ROOT / "apps"
if str(APPS) not in sys.path:
    sys.path.insert(0, str(APPS))

from mova.adapter.inbound.api.exception_handlers import (  # noqa: E402
    register_exception_handlers,
)
from mova.adapter.outbound.llm import gemini_client  # noqa: E402
from mova.app.exceptions import (  # noqa: E402
    LLMError,
    LLMTimeoutError,
    LLMUnavailableError,
)


class _NotReadyKeymaker:
    def is_gemini_ready(self) -> bool:
        return False


class GeminiClientExceptionTests(unittest.TestCase):
    def test_missing_key_raises_unavailable(self) -> None:
        with patch.object(gemini_client, "get_keymaker", return_value=_NotReadyKeymaker()):
            with self.assertRaises(LLMUnavailableError) as ctx:
                gemini_client.gemini_reply("안녕", None)
        # 기존 503 상태코드·메시지 보존
        self.assertEqual(ctx.exception.status_code, 503)
        self.assertIn("GEMINI_API_KEY", ctx.exception.detail)

    def test_exception_hierarchy(self) -> None:
        # 서브타입은 모두 LLMError 로 잡힌다 (핸들러 단일 등록 근거)
        self.assertTrue(issubclass(LLMUnavailableError, LLMError))
        self.assertTrue(issubclass(LLMTimeoutError, LLMError))
        self.assertEqual(LLMTimeoutError("x").status_code, 504)


class LLMErrorHandlerTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        register_exception_handlers(app)

        @app.get("/unavailable")
        async def _unavailable() -> dict[str, str]:
            raise LLMUnavailableError("Gemini 모델을 초기화할 수 없습니다.")

        @app.get("/quota")
        async def _quota() -> dict[str, str]:
            raise LLMError("할당량 초과", status_code=429)

        self.client = TestClient(app, raise_server_exceptions=False)

    def test_unavailable_returns_503(self) -> None:
        res = self.client.get("/unavailable")
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.json()["detail"], "Gemini 모델을 초기화할 수 없습니다.")

    def test_status_code_preserved(self) -> None:
        # LLMError 에 실린 상태코드가 그대로 매핑되어 503 으로 뭉개지지 않는다
        res = self.client.get("/quota")
        self.assertEqual(res.status_code, 429)
        self.assertEqual(res.json()["detail"], "할당량 초과")


if __name__ == "__main__":
    unittest.main()
