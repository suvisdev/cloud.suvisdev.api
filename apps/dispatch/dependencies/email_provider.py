from __future__ import annotations

import os

from core.lol.t1_mid_faker_orchestrator import get_faker_orchestrator
from dispatch.adapter.outbound.http.n8n_gmail_outbound import N8nGmailOutbound
from dispatch.app.ports.input.email_use_case import EmailUseCase
from dispatch.app.use_cases.send_email_interactor import SendEmailInteractor
from ontology.app.use_cases.hub_email_orchestrator import HubEmailOrchestrator


def get_email_use_case() -> EmailUseCase:
    webhook_url = os.getenv("N8N_DISPATCH_WEBHOOK_URL", "")
    if not webhook_url:
        raise RuntimeError(
            "N8N_DISPATCH_WEBHOOK_URL이 설정되지 않았습니다. suvisdev/.env를 확인하세요."
        )
    return SendEmailInteractor(
        gmail=N8nGmailOutbound(webhook_url=webhook_url),
        hub=HubEmailOrchestrator(),
        orchestrator=get_faker_orchestrator(),
    )
