import pytest

from unittest import mock

from hercules_sync.synchronization import OntologySynchronizer, GraphDiffSyncAlgorithm, \
                                          NaiveSyncAlgorithm

from .common import load_gitfile_from

SOURCE_FILE = 'source_props.ttl'
TARGET_FILE = 'target_props.ttl'

ASIO_PREFIX = 'http://www.asio.es/asioontologies/asio#'
EX_PREFIX = 'http://www.semanticweb.org/spitxa/ontologies/2020/1/asio-human-resource#'

@pytest.fixture(scope='module')
def input():
    return load_gitfile_from(SOURCE_FILE, TARGET_FILE)

@pytest.fixture
def mock_synchronizer():
    with mock.patch.object(OntologySynchronizer, '__init__', lambda slf, algorithm: None):
        synchronizer = OntologySynchronizer(None)
        synchronizer._algorithm = mock.MagicMock()
        synchronizer._annotate_triples = mock.MagicMock()
        yield synchronizer

@pytest.fixture
def operations_fixture(input):
    algorithm = GraphDiffSyncAlgorithm()
    return algorithm.do_algorithm(input)

def test_init():
    synchronizer = OntologySynchronizer(None)
    assert isinstance(synchronizer._algorithm, NaiveSyncAlgorithm)

    synchronizer = OntologySynchronizer(GraphDiffSyncAlgorithm())
    assert isinstance(synchronizer._algorithm, GraphDiffSyncAlgorithm)

def test_synchronize(mock_synchronizer):
    mock_synchronizer.synchronize(None)
    mock_synchronizer._algorithm.do_algorithm.assert_has_calls([mock.call(None)])

def test_etype_annotation(input):
    algorithm = GraphDiffSyncAlgorithm()
    ops = algorithm.do_algorithm(input)
    # check that original operations have default annotations
    for op in ops:
        for element in op._triple_info:
            if element.is_uri:
                assert element.etype == 'item'

    synchronizer = OntologySynchronizer(algorithm)
    annotated_ops = synchronizer._annotate_triples(ops, input)
    # check that now the subjects of this ontology are classified as properties
    for op in ops:
        triple_info = op._triple_info
        assert triple_info.subject.etype == 'property'

def test_synchronize_annotates_triples(mock_synchronizer):
    mock_synchronizer.synchronize(None)
    ops = mock_synchronizer._algorithm.do_algorithm(None)
    mock_synchronizer._annotate_triples.assert_has_calls([mock.call(ops, None)])
