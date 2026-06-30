from __future__ import annotations

from core.lol.t1_mid_faker_orchestrator import FakerOrchestratorError, T1MidFakerOrchestrator
from dispatch.adapter.inbound.api.schemas.email_schema import EmailIntroduceSchema
from dispatch.app.dtos.email_dto import EmailDto, EmailIntroduceQuery, EmailIntroduceResponse
from dispatch.app.ports.input.email_use_case import EmailUseCase
from dispatch.app.ports.output.dispatch_errors import DispatchError
from dispatch.app.ports.output.gmail_port import GmailPort
from ontology.app.use_cases.hub_email_orchestrator import HubEmailOrchestrator
from ontology.domain.events.spoke_events import DispatchEmailEvent

_DEFAULT_SUBJECT = "메일 발송"


class SendEmailInteractor(EmailUseCase):
    def __init__(
        self,
        *,
        gmail: GmailPort,
        hub: HubEmailOrchestrator,
        orchestrator: T1MidFakerOrchestrator,
    ) -> None:
        self._gmail = gmail
        self._hub = hub
        self._orchestrator = orchestrator

    _SYSTEM = (
        "당신은 이메일 본문 작성 전문가입니다. "
        "사용자의 지시에 따라 이메일 본문만 작성하세요. "
        "인사, 마무리 인사, 서명 등 완전한 이메일 형식으로 작성하세요. "
        "이메일 발송 기능 설명, 수신자 정보 안내, 추가 질문 없이 본문 내용만 반환하세요."
    )

    def send(self, *, to: str, prompt: str, subject: str | None) -> EmailDto:
        self._hub.record(DispatchEmailEvent(to=to, prompt=prompt, subject=subject))
        try:
            body = self._orchestrator.generate(prompt, system=self._SYSTEM)
        except FakerOrchestratorError as e:
            raise DispatchError(f"LLM 본문 생성 실패: {e.detail}", status_code=e.status_code) from e
        resolved_subject = (subject or _DEFAULT_SUBJECT).strip()
        self._gmail.send(to=to, subject=resolved_subject, body=body)
        return EmailDto(to=to, subject=resolved_subject, body=body)

    async def introduce_myself(self, schema: EmailIntroduceSchema) -> EmailIntroduceResponse:
        return await self._gmail.introduce_myself(
            EmailIntroduceQuery(id=schema.id, name=schema.name)
        )
