from typing import List

from hercules_sync.git import GitFile
from . import BaseSyncAlgorithm, NaiveSyncAlgorithm, SyncOperation
from ..triplestore import URIElement
from ..util.uri_constants import ASIO_BASE

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
        all_urielements = _extract_uris_from(ops)
        _annotate_uris_etype(all_urielements, source_model, target_model)
        _annotate_datatype_props(all_urielements, source_model, target_model)
        _annotate_object_props(all_urielements, source_model, target_model)

def _annotate_datatype_props(all_urielements, source_model, target_model):
    datatype_properties = source_model.all_properties_datatype + \
                          target_model.all_properties_datatype
    for urielement in all_urielements:
        for prop in datatype_properties:
            if urielement == str(prop.uri):
                if len(prop.ranges) > 0:
                    urielement.proptype = str(prop.ranges[0].uri)

def _annotate_object_props(all_urielements: List[URIElement], source_model, target_model):
    object_properties = source_model.all_properties_object + target_model.all_properties_object
    for urielement in all_urielements:
        for prop in object_properties:
            if urielement == str(prop.uri):
                if len(prop.ranges) > 0:
                    prop_range = prop.ranges[0]
                    urielement.proptype = f'{ASIO_BASE}property' \
                        if isinstance(prop_range, ontospy.core.entities.OntoProperty) \
                        else f'{ASIO_BASE}item'
                else:
                    # default type for object properties without range
                    urielement.proptype = f'{ASIO_BASE}item'

def _annotate_uris_etype(all_urielements: List[URIElement], source_model, target_model):
    properties = source_model.all_properties + target_model.all_properties
    properties_uris = list(map(lambda x: str(x.uri), properties))
    for urielement in all_urielements:
        if urielement in properties_uris:
            urielement.etype = 'property'

def _extract_uris_from(ops: List[SyncOperation]) -> List[URIElement]:
    return [el for op in ops
            for el in op._triple_info
            if el.is_uri]
