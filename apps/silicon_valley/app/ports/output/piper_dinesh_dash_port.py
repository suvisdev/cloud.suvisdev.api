from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery
from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashResponse

class DineshDashPort(ABC):
    """piper_dinesh_dash output port."""

    @abstractmethod
    def introduce_myself(self, query: DineshDashQuery)->DineshDashResponse:
        pass
