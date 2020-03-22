from typing import List

from hercules_sync.git import GitFile
from . import BaseSyncAlgorithm, NaiveSyncAlgorithm, SyncOperation

class OntologySynchronizer():
    """ Processes information from a GitHub push event.

    This class uses a syncrhonization algorithm to return the list of operations
    that need to be execute to synchronize a GitFile and a given triplestore.

    Parameters
    ----------
    algoritm : :obj:`BaseSyncAlgorithm`
        Algorithm that conforms to the BaseSyncAlgorithm interface.
    """

    def __init__(self, algorithm: BaseSyncAlgorithm):
        self._algorithm = algorithm if algorithm is not None else NaiveSyncAlgorithm()

    def synchronize(self, file: GitFile) -> List[SyncOperation]:
        """ Execute the algorithm to obtain the list of operations to execute.

        Parameters
        ----------
        file : :obj:`GitFile`
            GitFile object with information about the ontology file.

        Returns
        -------
        list of :obj:`SyncOperation`
            List of operations that need to be executed to synchronize the file
            with the triplestore.
        """
        return self._algorithm.do_algorithm(file)
