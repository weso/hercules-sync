from abc import ABC, abstractmethod

from ..triplestore import ModificationResult, TripleStoreManager, TripleInfo

class SyncOperation(ABC):
    """ Base class of all synchronization operations.

    Parameters
    ----------
    sub : str
        Subject of the triple to be synchronized.
    pred : str
        Predicate of the triple to be synchronized.
    obj : str
        Object of the triple to be synchronized.
    """
    def __init__(self, sub, pred, obj):
        self._triple_info = TripleInfo(sub, pred, obj)

    @abstractmethod
    def execute(self, triple_store: TripleStoreManager) -> ModificationResult:
        """ Executes the operation in the given triple store.

        Parameters
        ----------
        triple_store : :obj:`TripleStoreManager`
            Instance of triple store manager

        Returns
        -------
        :obj: `ModificationResult`
            Result given by the TripleStoreManager after the modification.

        """
        pass

    def __str__(self):
        return f"{self._triple_info.subject} \
                 {self._triple_info.predicate} \
                 {self._triple_info.object}"

class AdditionOperation(SyncOperation):
    def execute(self, triple_store: TripleStoreManager) -> ModificationResult:
        triple_store.create_triple(self._triple_info)

    def __str__(self):
        return "AdditionOperation: " + super(AdditionOperation, self).__str__()

class RemoveOperation(SyncOperation):
    def execute(self, triple_store: TripleStoreManager) -> ModificationResult:
        triple_store.remove_triple(self._triple_info)
