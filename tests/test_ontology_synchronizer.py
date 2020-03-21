import pytest

from unittest import mock

from hercules_sync.synchronization import OntologySynchronizer, GraphDiffSyncAlgorithm, \
                                          NaiveSyncAlgorithm

@pytest.fixture(scope='module')
def mock_synchronizer():
    with mock.patch.object(OntologySynchronizer, '__init__', lambda slf, algorithm: None):
        synchronizer = OntologySynchronizer(None)
        synchronizer._algorithm = mock.MagicMock()
        yield synchronizer

def test_init():
    synchronizer = OntologySynchronizer(None)
    assert isinstance(synchronizer._algorithm, NaiveSyncAlgorithm)

    synchronizer = OntologySynchronizer(GraphDiffSyncAlgorithm())
    assert isinstance(synchronizer._algorithm, GraphDiffSyncAlgorithm)

def test_synchronize(mock_synchronizer):
    mock_synchronizer.synchronize(None)
    mock_synchronizer._algorithm.do_algorithm.assert_has_calls([mock.call(None)])
