import os
import pdb

from pytest_bdd import scenarios, given, when, then
from unittest import mock

from wbsync.synchronization import AdditionOperation, RemovalOperation


scenarios('../features/change_triplestore.feature')

@given("the creation of a new triplestore adapter", target_fixture="triplestore")
def get_rdf_file():
    adapter = mock.MagicMock()
    adapter.create_triple = mock.MagicMock()
    adapter.remove_triple = mock.MagicMock()
    return adapter

@when("the triplestore is selected as the one to be synchronized")
def add_triples_to(triplestore):
    pass

@then("the synchronization operations are executed on the new triplestore")
def confirm_triples_addition(triplestore):
    ops = _generate_test_ops()
    for op in ops:
        op.execute(triplestore)
    triplestore.remove_triple.assert_called_once()
    assert triplestore.create_triple.call_count == 2

def _generate_test_ops():
    return [AdditionOperation(None, None, None), 
            AdditionOperation(None, None, None),
            RemovalOperation(None, None, None)]