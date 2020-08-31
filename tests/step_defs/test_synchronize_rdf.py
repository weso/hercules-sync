import os
import pdb

from pytest_bdd import scenarios, given, when, then
from unittest import mock

from hercules_sync.git import GitFile
from wbsync.synchronization import GraphDiffSyncAlgorithm, OntologySynchronizer, \
                                          AdditionOperation, RemovalOperation
from wbsync.triplestore import WikibaseAdapter


DATA_DIR = os.path.join(os.path.join('tests', 'data'), 'synchronization')
SRC_RDF_FILENAME = 'source.ttl'

scenarios('../features/synchronize_rdf.feature')

def _parse_test_rdf_file():
    src_content = ""
    with open(os.path.join(DATA_DIR, SRC_RDF_FILENAME), 'r') as f:
        src_content = f.read()
    return GitFile(None, src_content, "")

@given("an RDF file", target_fixture="gitfile")
def get_rdf_file():
    return _parse_test_rdf_file()

@when("a new triple is added to the file")
def add_triples_to(gitfile):
    with open(os.path.join(DATA_DIR, 'addition.ttl'), 'r') as f:
        gitfile.target_content = f.read()

@then("the triple will be added to the Wikibase")
def confirm_triples_addition(gitfile, mocked_adapter):
    ops = _perform_sync(gitfile, mocked_adapter)
    _assert_wb_called(mocked_adapter)
    assert len(ops) == 1
    assert isinstance(ops[0], AdditionOperation)

@when("an existing triple is removed from the file")
def remove_triples_from(gitfile):    
    with open(os.path.join(DATA_DIR, 'removal.ttl'), 'r') as f:
        gitfile.target_content = f.read()

@then("the corresponding triple will be removed from the Wikibase")
def confirm_triples_removal(gitfile, mocked_adapter):
    ops = _perform_sync(gitfile, mocked_adapter)
    _assert_wb_called(mocked_adapter)
    assert len(ops) == 1
    assert isinstance(ops[0], RemovalOperation)

@when("the contents of a triple are modified")
def modify_triples_from(gitfile, mocked_adapter):
    with open(os.path.join(DATA_DIR, 'modification.ttl'), 'r') as f:
        gitfile.target_content = f.read()

@then("the modifications will be synchronized with the Wikibase")
def confirm_triples_modification(gitfile, mocked_adapter):
    ops = _perform_sync(gitfile, mocked_adapter)
    _assert_wb_called(mocked_adapter)
    assert len(ops) == 2
    assert isinstance(ops[0], RemovalOperation)
    assert isinstance(ops[1], AdditionOperation)

def _assert_wb_called(adapter):
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # fetch subject
        mock.call('Q1'),
        # create object
        mock.call(new_item=True),
        # create predicate
        mock.call(new_item=True),
    ]
    adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False) 

def _perform_sync(gitfile, mocked_adapter):
    algorithm = GraphDiffSyncAlgorithm()
    synchronizer = OntologySynchronizer(algorithm)
    ops = synchronizer.synchronize(gitfile.source_content, gitfile.target_content)
    for op in ops:
        res = op.execute(mocked_adapter)
    return ops
