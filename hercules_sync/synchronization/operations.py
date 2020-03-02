from abc import ABC, abstractmethod

from . import TripleInfo

class SyncOperation(ABC):
    """
    """
    def __init__(self, sub, pred, obj):
        self._triple_info = TripleInfo(sub, pred, obj)

    @abstractmethod
    def execute(self, triple_store):
        pass

    def __str_(self):
        return f"#{self._triple_info.subject} \
                 #{self._triple_info.predicate} \
                 #{self._triple_info.object}"

class AdditionOperation(SyncOperation):
    def execute(self, triple_store):
        pass

    def __str__(self):
        return "AdditionOperation: " + super(AdditionOperation, self).__str__()

class RemoveOperation(SyncOperation):
    def execute(self, triple_store):
        pass
