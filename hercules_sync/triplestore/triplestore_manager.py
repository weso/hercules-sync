from abc import ABC, abstractmethod

from . import TripleInfo

class ModificationResult():
    def __init__(self, successful: bool, message: str):
        self.successful = successful
        self.message = message

class TripleStoreManager(ABC):

    @abstractmethod
    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    @abstractmethod
    def modify_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    @abstractmethod
    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass
