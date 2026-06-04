from abc import ABC, abstractmethod

from titanic.app.dtos.walter_dto import WalterQuery

class WalterRepository(ABC):

    @abstractmethod
    def introduce_myself(self, query: WalterQuery):
        pass