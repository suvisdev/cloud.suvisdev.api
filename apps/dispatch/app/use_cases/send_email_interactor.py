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
        "사용자의 지시에 따라 완성된 이메일 본문만 작성하세요. "
        "인사말, 본문, 마무리 인사까지 완전한 이메일 형식으로 작성하세요. "
        "[수신자 이름], [프로젝트 이름] 같은 대괄호 플레이스홀더는 절대 사용하지 마세요. "
        "정보가 없으면 합리적으로 추측하거나 일반적인 표현으로 대체하세요. "
        "마크다운 문법(**굵게**, ##제목 등)은 사용하지 마세요. 일반 텍스트로만 작성하세요. "
        "이메일 본문 외 설명, 안내, 추가 질문은 절대 포함하지 마세요."
    )

    def send(self, *, to: str, prompt: str, subject: str | None) -> EmailDto:
        self._hub.record(DispatchEmailEvent(to=to, prompt=prompt, subject=subject))
        full_prompt = f"수신자 이메일: {to}\n\n지시사항: {prompt}"
        try:
            body = self._orchestrator.generate(full_prompt, system=self._SYSTEM)
        except FakerOrchestratorError as e:
            raise DispatchError(f"LLM 본문 생성 실패: {e.detail}", status_code=e.status_code) from e
        resolved_subject = (subject or _DEFAULT_SUBJECT).strip()
        self._gmail.send(to=to, subject=resolved_subject, body=body)
        return EmailDto(to=to, subject=resolved_subject, body=body)

    async def introduce_myself(self, schema: EmailIntroduceSchema) -> EmailIntroduceResponse:
        return await self._gmail.introduce_myself(
            EmailIntroduceQuery(id=schema.id, name=schema.name)
        )
