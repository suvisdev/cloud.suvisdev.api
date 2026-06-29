from __future__ import annotations

from core.lol.t1_mid_faker_orchestrator import FakerOrchestratorError, T1MidFakerOrchestrator
from dispatch.app.dtos.email_dto import EmailDto
from dispatch.app.ports.output.dispatch_errors import DispatchError
from dispatch.app.ports.output.gmail_port import GmailPort

_DEFAULT_SUBJECT = "메일 발송"


class SendEmailInteractor:
    def __init__(self, *, gmail: GmailPort, orchestrator: T1MidFakerOrchestrator) -> None:
        self._gmail = gmail
        self._orchestrator = orchestrator

    def send(self, *, to: str, prompt: str, subject: str | None) -> EmailDto:
        try:
            body = self._orchestrator.generate(prompt)
        except FakerOrchestratorError as e:
            raise DispatchError(f"LLM 본문 생성 실패: {e.detail}", status_code=e.status_code) from e
        resolved_subject = (subject or _DEFAULT_SUBJECT).strip()
        self._gmail.send(to=to, subject=resolved_subject, body=body)
        return EmailDto(to=to, subject=resolved_subject, body=body)
