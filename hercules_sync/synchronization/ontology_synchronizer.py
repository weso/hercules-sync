from typing import List

from hercules_sync.git import GitFile
from . import BaseSyncAlgorithm, NaiveSyncAlgorithm, SyncOperation

class OntologySynchronizer():

    def __init__(self, algorithm: BaseSyncAlgorithm):
        self._algorithm = algorithm if algorithm is not None else NaiveSyncAlgorithm()

    def synchronize(self, file: GitFile) -> List[SyncOperation]:
        return self._algorithm.do_algorithm(file)
