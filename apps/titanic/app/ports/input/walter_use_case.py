from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.walter_schema import WalterSchema

class WalterUseCase(ABC):
    @abstractmethod
    def introduce_myself(self, schemas: WalterSchema):
        pass