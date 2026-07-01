"""왓슨(Watson) — 인바운드 게이트웨이 & 초진 분류(Triage) 관문.

경찰 레이어(telegram·discord 등)에서 이벤트를 후킹해 발신자·본문을 가볍게 분석하고,
일반 업무는 Holmes(dispatch 내부)에게, 중요/보고서 요청은 온톨로지 버스를 경유해
페이커(EXAONE)에게 격상한다.
"""

from __future__ import annotations

import logging

from dispatch.app.use_cases.holmes_interactor import HolmesInteractor
from ontology.app.use_cases.hub_report_orchestrator import HubReportOrchestrator
from ontology.domain.events.spoke_events import InboundMessageEvent

logger = logging.getLogger(__name__)

# 보고서·에스컬레이션 의도를 나타내는 키워드
_ESCALATION_KEYWORDS = ("보고서", "리포트", "report", "실적", "발행")


class DetectiveWatsonWatcherHub:
    """Triage Nurse — 인입 메시지를 1차 분류하고 라우팅한다."""

    def __init__(
        self,
        *,
        holmes: HolmesInteractor,
        hub_report: HubReportOrchestrator,
    ) -> None:
        self._holmes = holmes
        self._hub_report = hub_report

    def watch(self, event: InboundMessageEvent) -> str:
        logger.info(
            "[dispatch Watson] 👀 이벤트 후킹 | channel=%s sender=%s vip=%s",
            event.channel,
            event.sender,
            event.important_client,
        )
        if self._needs_escalation(event):
            logger.info("[dispatch Watson] 🚨 Case B(중요/보고서) — 온톨로지 버스로 격상")
            return self._hub_report.escalate(event)
        logger.info("[dispatch Watson] 📎 Case A(일반) — Holmes에게 위임")
        return self._holmes.resolve(event)

    def _needs_escalation(self, event: InboundMessageEvent) -> bool:
        if event.important_client:
            return True
        body = event.body.lower()
        return any(keyword.lower() in body for keyword in _ESCALATION_KEYWORDS)
