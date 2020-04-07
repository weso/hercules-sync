from typing import List

from hercules_sync.git import GitFile
from . import BaseSyncAlgorithm, NaiveSyncAlgorithm, SyncOperation
from ..triplestore import URIElement

import ontospy

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
        ops = self._algorithm.do_algorithm(file)
        self._annotate_triples(ops, file)
        return ops

    def _annotate_triples(self, ops: List[SyncOperation], file: GitFile):
        source_model = ontospy.Ontospy(data=file.source_content, rdf_format='ttl')
        target_model = ontospy.Ontospy(data=file.target_content, rdf_format='ttl')
        properties = source_model.all_properties + target_model.all_properties
        properties_uris = list(map(lambda x: str(x.uri), properties))
        all_urielements = self._extract_uris_from(ops)
        for urielement in all_urielements:
            if urielement in properties_uris:
                urielement.etype = 'property'


    def _extract_uris_from(self, ops: List[SyncOperation]):
        return [el for op in ops
                for el in op._triple_info
                if el.is_uri]
