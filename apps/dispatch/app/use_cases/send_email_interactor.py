from __future__ import annotations

import re

from core.lol.t1_mid_faker_orchestrator import FakerOrchestratorError, T1MidFakerOrchestrator
from dispatch.adapter.inbound.api.schemas.email_schema import EmailIntroduceSchema
from dispatch.app.dtos.email_dto import EmailDto, EmailIntroduceQuery, EmailIntroduceResponse
from dispatch.app.ports.input.email_use_case import EmailUseCase
from dispatch.app.ports.output.dispatch_errors import DispatchError
from dispatch.app.ports.output.gmail_port import GmailPort
from ontology.app.use_cases.hub_email_orchestrator import HubEmailOrchestrator
from ontology.domain.events.spoke_events import DispatchEmailEvent

_DEFAULT_SUBJECT = "메일 발송"

# exaone3.5:2.4b는 프롬프트로 금지해도 대괄호 플레이스홀더·마크다운을 종종 남긴다.
# 시스템 프롬프트만으로는 신뢰할 수 없어 출력을 한 번 더 정리한다.
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_HEADER_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")
_PLACEHOLDER_RE = re.compile(r"\[[^\[\]\n]{1,40}\]")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def _sanitize_body(text: str) -> str:
    text = _PLACEHOLDER_RE.sub("", text)
    text = _BOLD_RE.sub(r"\1", text)
    text = _ITALIC_RE.sub(r"\1", text)
    text = _HEADER_RE.sub("", text)
    lines = [re.sub(r"[ \t]{2,}", " ", line).strip() for line in text.split("\n")]
    return _BLANK_LINES_RE.sub("\n\n", "\n".join(lines)).strip()


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

    _SUBJECT_SYSTEM = (
        "당신은 이메일 제목 작성 전문가입니다. "
        "사용자의 지시 내용을 한눈에 알 수 있는 이메일 제목을 한 줄로만 작성하세요. "
        "따옴표, 대괄호, 마크다운, 설명은 절대 포함하지 말고 제목 텍스트만 출력하세요."
    )

    def send(self, *, to: str, prompt: str, subject: str | None) -> EmailDto:
        self._hub.record(DispatchEmailEvent(to=to, prompt=prompt, subject=subject))
        full_prompt = f"수신자 이메일: {to}\n\n지시사항: {prompt}"
        try:
            body = self._orchestrator.generate(full_prompt, system=self._SYSTEM)
        except FakerOrchestratorError as e:
            raise DispatchError(f"LLM 본문 생성 실패: {e.detail}", status_code=e.status_code) from e
        body = _sanitize_body(body)
        resolved_subject = (subject or "").strip() or self._generate_subject(prompt)
        self._gmail.send(to=to, subject=resolved_subject, body=body)
        return EmailDto(to=to, subject=resolved_subject, body=body)

    def _generate_subject(self, prompt: str) -> str:
        try:
            generated = self._orchestrator.generate(prompt, system=self._SUBJECT_SYSTEM)
        except FakerOrchestratorError:
            return _DEFAULT_SUBJECT
        cleaned = _sanitize_body(generated).strip("\"'")
        return cleaned or _DEFAULT_SUBJECT

    async def introduce_myself(self, schema: EmailIntroduceSchema) -> EmailIntroduceResponse:
        return await self._gmail.introduce_myself(
            EmailIntroduceQuery(id=schema.id, name=schema.name)
        )
