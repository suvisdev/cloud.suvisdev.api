from __future__ import annotations

from typing import Protocol

from titanic.app.use_cases.caledon_validation import TitanicPredictInput, TitanicPredictOutput


class TitanicCommandPort(Protocol):
    """타이타닉 명령(Command) 인바운드 포트."""

    def predict(self, payload: TitanicPredictInput) -> TitanicPredictOutput: ...
