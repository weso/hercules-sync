from abc import ABC, abstractmethod

from ..triplestore import ModificationResult, TripleStoreManager, TripleElement, TripleInfo

class SyncOperation(ABC):
    """ Base class of all synchronization operations.

    Parameters
    ----------
    sub : TripleElement
        Subject of the triple to be synchronized.
    pred : TripleElement
        Predicate of the triple to be synchronized.
    obj : TripleElement
        Object of the triple to be synchronized.
    """
    def __init__(self, sub: TripleElement, pred: TripleElement, obj: TripleElement):
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

    def __str__(self):
        return f"{self._triple_info.subject} - {self._triple_info.predicate} " \
               + f"- {self._triple_info.object}"

class AdditionOperation(SyncOperation):
    def execute(self, triple_store: TripleStoreManager) -> ModificationResult:
        triple_store.create_triple(self._triple_info)

    def __str__(self):
        return "AdditionOperation: " + super(AdditionOperation, self).__str__()

    def __eq__(self, other):
        if not isinstance(other, AdditionOperation):
            return False

        return self._triple_info == other._triple_info

class RemovalOperation(SyncOperation):
    def execute(self, triple_store: TripleStoreManager) -> ModificationResult:
        triple_store.remove_triple(self._triple_info)

    def __str__(self):
        return "RemovalOperation: " + super(RemovalOperation, self).__str__()

    def __eq__(self, other):
        if not isinstance(other, RemovalOperation):
            return False

        return self._triple_info == other._triple_info
