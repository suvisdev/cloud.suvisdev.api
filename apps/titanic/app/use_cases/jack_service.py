"""이전 모듈 경로 호환 — `train_use_case.JackService` 재노출."""

from titanic.app.use_cases.train_use_case import JackService

__all__ = ["JackService"]
