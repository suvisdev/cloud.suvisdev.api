from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from dispatch.app.dtos.email_dto import EmailDto


class EmailUseCase(Protocol):
    def send(self, *, to: str, prompt: str, subject: str | None) -> EmailDto: ...
