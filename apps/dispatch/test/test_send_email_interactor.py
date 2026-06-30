from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[3]
APPS = ROOT / "apps"
if str(APPS) not in sys.path:
    sys.path.insert(0, str(APPS))

from core.lol.t1_mid_faker_orchestrator import (  # noqa: E402
    FakerOrchestratorError,
    T1MidFakerOrchestrator,
)
from dispatch.app.dtos.email_dto import EmailDto  # noqa: E402
from dispatch.app.ports.output.dispatch_errors import DispatchError  # noqa: E402
from dispatch.app.ports.output.gmail_port import GmailPort  # noqa: E402
from dispatch.app.use_cases.send_email_interactor import SendEmailInteractor  # noqa: E402
from ontology.app.use_cases.hub_email_orchestrator import HubEmailOrchestrator  # noqa: E402
from ontology.domain.events.spoke_events import DispatchEmailEvent  # noqa: E402


class SendEmailInteractorTest(unittest.TestCase):
    def _make_interactor(
        self,
        orc_body: str = "생성된 본문",
    ) -> tuple[SendEmailInteractor, MagicMock, MagicMock, MagicMock]:
        mock_hub: MagicMock = MagicMock(spec=HubEmailOrchestrator)
        mock_orc: MagicMock = MagicMock(spec=T1MidFakerOrchestrator)
        mock_orc.generate.return_value = orc_body
        mock_gmail: MagicMock = MagicMock(spec=GmailPort)
        interactor = SendEmailInteractor(gmail=mock_gmail, hub=mock_hub, orchestrator=mock_orc)
        return interactor, mock_hub, mock_orc, mock_gmail

    def test_hub_record_called_before_orchestrator(self) -> None:
        interactor, mock_hub, mock_orc, _ = self._make_interactor()
        call_order: list[str] = []
        mock_hub.record.side_effect = lambda _: call_order.append("hub")
        mock_orc.generate.side_effect = lambda _: call_order.append("orc") or "본문"

        interactor.send(to="a@b.com", prompt="p", subject="s")

        self.assertEqual(call_order, ["hub", "orc"])

    def test_hub_receives_correct_event(self) -> None:
        interactor, mock_hub, _, _ = self._make_interactor()

        interactor.send(to="a@b.com", prompt="write email", subject="제목")

        called_event: DispatchEmailEvent = mock_hub.record.call_args[0][0]
        self.assertIsInstance(called_event, DispatchEmailEvent)
        self.assertEqual(called_event.to, "a@b.com")
        self.assertEqual(called_event.prompt, "write email")
        self.assertEqual(called_event.subject, "제목")

    def test_orchestrator_generates_body(self) -> None:
        interactor, _, mock_orc, mock_gmail = self._make_interactor(orc_body="LLM이 쓴 본문")

        interactor.send(to="a@b.com", prompt="p", subject="제목")

        mock_orc.generate.assert_called_once_with("p")
        mock_gmail.send.assert_called_once_with(to="a@b.com", subject="제목", body="LLM이 쓴 본문")

    def test_send_returns_email_dto(self) -> None:
        interactor, _, _, _ = self._make_interactor(orc_body="본문")

        dto = interactor.send(to="x@y.com", prompt="p", subject="공지")

        self.assertIsInstance(dto, EmailDto)
        self.assertEqual(dto.to, "x@y.com")
        self.assertEqual(dto.subject, "공지")
        self.assertEqual(dto.body, "본문")

    def test_default_subject_when_none(self) -> None:
        interactor, _, _, mock_gmail = self._make_interactor()

        interactor.send(to="a@b.com", prompt="p", subject=None)

        _, kwargs = mock_gmail.send.call_args
        self.assertEqual(kwargs["subject"], "메일 발송")

    def test_orchestrator_error_raises_dispatch_error(self) -> None:
        _, mock_hub, mock_orc, _ = (
            MagicMock(spec=HubEmailOrchestrator),
            MagicMock(spec=HubEmailOrchestrator),
            MagicMock(spec=T1MidFakerOrchestrator),
            MagicMock(spec=GmailPort),
        )
        mock_orc.generate.side_effect = FakerOrchestratorError("타임아웃", status_code=504)
        interactor = SendEmailInteractor(
            gmail=MagicMock(spec=GmailPort), hub=mock_hub, orchestrator=mock_orc
        )

        with self.assertRaises(DispatchError) as ctx:
            interactor.send(to="a@b.com", prompt="p", subject=None)

        self.assertEqual(ctx.exception.status_code, 504)
        self.assertIn("LLM 본문 생성 실패", ctx.exception.detail)

    def test_gmail_not_called_when_orchestrator_fails(self) -> None:
        mock_hub: MagicMock = MagicMock(spec=HubEmailOrchestrator)
        mock_orc: MagicMock = MagicMock(spec=T1MidFakerOrchestrator)
        mock_orc.generate.side_effect = FakerOrchestratorError("err", status_code=503)
        mock_gmail: MagicMock = MagicMock(spec=GmailPort)
        interactor = SendEmailInteractor(gmail=mock_gmail, hub=mock_hub, orchestrator=mock_orc)

        with self.assertRaises(DispatchError):
            interactor.send(to="a@b.com", prompt="p", subject=None)

        mock_gmail.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
