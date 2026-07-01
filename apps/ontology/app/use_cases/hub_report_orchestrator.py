"""Hub 에스컬레이션 — 중요/보고서 요청을 최고 사령탑(Faker/EXAONE)으로 격상.

Spoke(dispatch)의 Watson이 격상 판단을 내리면, 온톨로지 버스(ontology)를 경유해
core/lol의 페이커(EXAONE) 오케스트레이터를 기상(wake-up)시켜 전사 보고서를 생성한다.
"""

from __future__ import annotations

import logging

from core.lol.t1_mid_faker_orchestrator import (
    FakerOrchestratorError,
    T1MidFakerOrchestrator,
)
from ontology.domain.events.spoke_events import InboundMessageEvent

logger = logging.getLogger(__name__)

_REPORT_SYSTEM = (
    "당신은 전사 ERP 데이터를 취합하는 최고 분석 에이전트입니다. "
    "요청에 대한 간결한 실적 보고서 초안을 한국어로 작성하세요. "
    "불필요한 안내·질문 없이 보고서 본문만 반환하세요."
)


class HubReportOrchestrator:
    """온톨로지 버스 → 페이커(EXAONE) 격상 파이프라인."""

    def __init__(self, *, orchestrator: T1MidFakerOrchestrator) -> None:
        self._orchestrator = orchestrator

    def escalate(self, event: InboundMessageEvent) -> str:
        logger.info(
            "[ontology Hub] ⭐ 온톨로지 버스 경유 — VIP 이벤트 격상 | sender=%s",
            event.sender,
        )
        logger.info("[core/lol Faker] 🧠 페이커(EXAONE) 기상 — 전사 보고서 생성 착수")
        try:
            report = self._orchestrator.generate(event.body, system=_REPORT_SYSTEM)
        except FakerOrchestratorError as e:
            logger.warning(
                "[core/lol Faker] ⚠️ EXAONE 호출 실패(%s) — 하네스 폴백 보고서로 대체",
                e.detail,
            )
            report = f"[폴백 보고서] '{event.body}' 요청 접수 — EXAONE 미가동 상태"
        logger.info("[core/lol Faker] ✅ 보고서 생성 완료 — 스포크로 하향 전달")
        return report
