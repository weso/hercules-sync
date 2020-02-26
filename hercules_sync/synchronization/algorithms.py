from abc import ABC, abstractmethod
from typing import List

from hercules_sync.git import GitFile
from hercules_sync.synchronization import SyncOperation

class BaseAlgorithm(ABC):
    """ Base class for all synchronization algorithms.

    Parameters
    ----------
    file : `obj`:GitFile
        GitFile object with information about the diff.
    """

    def __init__(self, file: GitFile):
        self.file = file

    @abstractmethod
    def algorithm(self) -> List[SyncOperation]:
        """
        """
        pass

class NaiveAlgorithm(BaseAlgorithm):
    pass

class RDFSyncAlgorithm(BaseAlgorithm):
    pass
