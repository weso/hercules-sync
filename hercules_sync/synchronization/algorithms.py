
from abc import ABC, abstractmethod
from typing import List

from rdflib.compare import graph_diff, to_isomorphic
from rdflib.graph import Graph

from hercules_sync.git import GitFile
from hercules_sync.triplestore import TripleInfo
from . import AdditionOperation, RemovalOperation, SyncOperation

class BaseSyncAlgorithm(ABC):
    """ Base class for all synchronization algorithms.

    Parameters
    ----------
    file : `obj`:GitFile
        GitFile object with information about the diff.
    """

    def __init__(self):
        pass

    @abstractmethod
    def do_algorithm(self, file: GitFile) -> List[SyncOperation]:
        """
        """

class NaiveSyncAlgorithm(BaseSyncAlgorithm):
    def do_algorithm(self, file: GitFile) -> List[SyncOperation]:
        raise NotImplementedError("NaiveSync algorithm has not been implemented yet.")

class GraphDiffSyncAlgorithm(BaseSyncAlgorithm):
    def do_algorithm(self, file: GitFile) -> List[SyncOperation]:
        source_g = Graph().parse(format='turtle', data=file.source_content)
        target_g = Graph().parse(format='turtle', data=file.target_content)
        source_g_iso = to_isomorphic(source_g)
        target_g_iso = to_isomorphic(target_g)
        _, removals_graph, additions_graph = graph_diff(source_g_iso,
                                                        target_g_iso)
        additions_ops = self._create_add_ops_from(additions_graph)
        removals_ops = self._create_remove_ops_from(removals_graph)
        return additions_ops + removals_ops

    def _create_add_ops_from(self, graph: Graph) -> List[AdditionOperation]:
        return [AdditionOperation(*TripleInfo.from_rdflib(triple).content)
                for triple in graph]

    def _create_remove_ops_from(self, graph: Graph) -> List[RemovalOperation]:
        return [RemovalOperation(*TripleInfo.from_rdflib(triple).content)
                for triple in graph]

class RDFSyncAlgorithm(BaseSyncAlgorithm):
    def do_algorithm(self, file: GitFile) -> List[SyncOperation]:
        raise NotImplementedError("RDFSync algorithm has not been implemented yet.")
