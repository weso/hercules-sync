from unittest import mock

import logging
import pytest

from wikidataintegrator import wdi_core

from hercules_sync.external.uri_factory_mock import URIFactory
from hercules_sync.triplestore import URIElement, LiteralElement, ModificationResult, \
                                      TripleInfo, WikibaseAdapter
from hercules_sync.triplestore.wikibase_adapter import DEFAULT_LANG, is_asio_uri
from hercules_sync.util.uri_constants import ASIO_BASE, GEO_BASE, RDFS_LABEL, RDFS_COMMENT, \
                                             SKOS_ALTLABEL, SCHEMA_NAME, SCHEMA_DESCRIPTION, \
                                             SKOS_PREFLABEL

FACTORY = URIFactory()

class IDGenerator():
    def __init__(self):
        self.curr_id = 0

    def generate_id(self, _, **kwargs):
        try:
            etype = kwargs['entity_type']
            self.curr_id += 1
            str_id = str(self.curr_id)
            return 'Q' + str_id if etype == 'item' else 'P' + str_id
        except KeyError:
            pass

@pytest.fixture()
def id_generator():
    return IDGenerator()

@pytest.fixture(autouse=True)
def reset_state(id_generator):
    id_generator.curr_id = 0
    FACTORY.reset_factory()

@pytest.fixture
def mocked_adapter(id_generator):
    with mock.patch.object(WikibaseAdapter, '__init__', lambda slf, a, b, c, d: None):
        adapter = WikibaseAdapter('', '', '', '')
        writer_mock = mock.MagicMock()
        writer_mock.write = mock.MagicMock(side_effect=id_generator.generate_id)
        adapter._local_item_engine = mock.MagicMock(return_value=writer_mock)
        adapter._local_login = mock.MagicMock()
        adapter._mappings_prop = mock.MagicMock()
        adapter._add_mappings_to_entity = mock.MagicMock()
        yield adapter

@pytest.fixture
def triples():
    example = 'https://example.org/onto#'
    example_no_hashtag = 'https://example.org/onto/'
    example_no_label = 'example'
    example_asio = 'https://example.org/hercules/asio#'

    return {
        'alias_en': TripleInfo(URIElement(example + 'Person'), URIElement(SKOS_ALTLABEL),
                              LiteralElement('individual', lang='en')),
        'alias_es': TripleInfo(URIElement(example + 'Person'), URIElement(SKOS_ALTLABEL),
                              LiteralElement('individuo', lang='es')),
        'alias_es_2': TripleInfo(URIElement(example + 'Person'), URIElement(SKOS_ALTLABEL),
                              LiteralElement('sujeto', lang='es')),
        'desc_en': TripleInfo(URIElement(example + 'Person'), URIElement(RDFS_COMMENT),
                              LiteralElement('A person', lang='en')),
        'desc_es': TripleInfo(URIElement(example + 'Person'), URIElement(RDFS_COMMENT),
                              LiteralElement('Una persona', lang='es')),
        'desc_long': TripleInfo(URIElement(example + 'Person'), URIElement(RDFS_COMMENT),
                              LiteralElement('Una persona' * 500, lang='es')),
        'desc_asio': TripleInfo(URIElement(example_asio + 'authors'), URIElement(RDFS_COMMENT),
                              LiteralElement('Publication authored by a person.', lang='en')),
        'label_en': TripleInfo(URIElement(example + 'labra'), URIElement(RDFS_LABEL),
                               LiteralElement('Jose Emilio Labra Gayo', lang='en')),
        'label_ko': TripleInfo(URIElement(example + 'labra'), URIElement(RDFS_LABEL),
                               LiteralElement('라브라', lang='ko')),
        'label_no_lang': TripleInfo(URIElement(example + 'labra'), URIElement(RDFS_LABEL),
                               LiteralElement('José Emilio Labra Gayo')),
        'label_unknown': TripleInfo(URIElement(example + 'labra'), URIElement(RDFS_LABEL),
                                    LiteralElement('라브', lang='invented')),
        'literal_datatype': TripleInfo(URIElement(example + 'Person'), URIElement(example + 'livesIn'),
                                       LiteralElement('Point(12.34 2.43)', datatype=f"{GEO_BASE}wktLiteral")),
        'no_label': TripleInfo(URIElement(example_no_label + 'test'), URIElement(RDFS_LABEL),
                               LiteralElement('a test', lang='en')),
        'no_hashtag': TripleInfo(URIElement(example_no_hashtag + 'test'), URIElement(RDFS_LABEL),
                               LiteralElement('1234', lang='en')),
        'proptype': TripleInfo(URIElement(example + 'test', etype='property', proptype=f"{ASIO_BASE}property"),
                               URIElement(RDFS_LABEL), LiteralElement('test')),
        'wditemid': TripleInfo(URIElement(example + 'Person'), URIElement(example + 'livesIn'),
                               URIElement(example + 'City')),
        'wdstring': TripleInfo(URIElement(example + 'Person'), URIElement(example + 'altName'),
                               LiteralElement('Human'))
    }

def raise_wdapierror(err_msg):
    raise wdi_core.WDApiError(err_msg)


def test_alternative_description_uris(mocked_adapter, triples):
    desc_en = triples['desc_en']
    desc_en.predicate.uri = SCHEMA_DESCRIPTION
    mocked_adapter.create_triple(desc_en)

    writer = mocked_adapter._local_item_engine(None)
    set_desc_calls = [mock.call('A person', 'en')]
    writer.set_description.assert_has_calls(set_desc_calls, any_order=False)

def test_alternative_label_uris(mocked_adapter, triples):
    label_en = triples['label_en']
    label_ko = triples['label_ko']
    label_en.predicate.uri = SKOS_PREFLABEL
    label_ko.predicate.uri = SCHEMA_NAME
    mocked_adapter.create_triple(label_en)
    mocked_adapter.create_triple(label_ko)

    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        # default URI label
        mock.call('labra'),
        # label created with skos:preflabel predicate
        mock.call('Jose Emilio Labra Gayo', 'en'),
        # label created with schema:name predicate
        mock.call('라브라', 'ko')
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)

def test_create_triple(mocked_adapter, triples):
    new_triple = triples['wditemid']
    mocked_adapter.create_triple(new_triple)
    item_engine_calls = [
        mock.call(new_item=True),
        mock.call(new_item=True),
        mock.call(new_item=True),
        mock.call('Q1', data=[new_triple.object.to_wdi_datatype(prop_nr=new_triple.predicate.id)],
                  append_value=[new_triple.predicate.id])
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False)

    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        mock.call("Person"),
        mock.call("City"),
        mock.call("livesIn")
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)

    login = mocked_adapter._local_login
    write_calls = [
        mock.call(login, entity_type='item', property_datatype=None),
        mock.call(login, entity_type='item', property_datatype=None),
        mock.call(login, entity_type='property', property_datatype='wikibase-item'),
        mock.call(login, entity_type='item', property_datatype='wikibase-item')
    ]
    writer.write.assert_has_calls(write_calls, any_order=False)

def test_existing_entity_is_not_created_again(mocked_adapter, triples):
    triple_a = triples['wditemid']
    triple_b = triples['wdstring']
    mocked_adapter.create_triple(triple_a)
    mocked_adapter.create_triple(triple_b)
    item_engine_calls = [
        # subject from triple_a
        mock.call(new_item=True),
        # object from triple_a
        mock.call(new_item=True),
        # predicate from triple_a
        mock.call(new_item=True),
        # statement from triple_a
        mock.call('Q1', data=[triple_a.object.to_wdi_datatype(prop_nr=triple_a.predicate.id)],
                  append_value=[triple_a.predicate.id]),
        # predicate from triple_b
        mock.call(new_item=True),
        # statement from triple_b
        mock.call('Q1', data=[triple_b.object.to_wdi_datatype(prop_nr=triple_b.predicate.id)],
                  append_value=[triple_b.predicate.id])
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls)

def test_is_asio_uri(triples):
    assert is_asio_uri(triples['desc_asio'].subject)
    assert not is_asio_uri(triples['desc_asio'].predicate)
    assert not is_asio_uri(triples['desc_en'].subject)

def test_label_cant_be_inferred(mocked_adapter, triples):
    triple = triples['no_label']
    mocked_adapter.create_triple(triple)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # create label for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False)

    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        # label created with rdfs:label predicate
        mock.call('a test', 'en')
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)
    assert writer.set_label.call_count == 1

def test_label_no_lang_uses_default_lang(mocked_adapter, triples):
    triple = triples['label_no_lang']
    mocked_adapter.create_triple(triple)
    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        # inferred label
        mock.call('labra'),
        # label created with rdfs:label predicate
        mock.call('José Emilio Labra Gayo', DEFAULT_LANG)
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)
    assert writer.set_label.call_count == 2

def test_label_with_no_hashtag_is_inferred(mocked_adapter, triples):
    triple = triples['no_hashtag']
    mocked_adapter.create_triple(triple)
    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        # inferred label
        mock.call('test'),
        # label created with rdfs:label predicate
        mock.call('1234', 'en')
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)
    assert writer.set_label.call_count == 2

def test_long_description_is_shortened(mocked_adapter, triples):
    triple = triples['desc_long']
    mocked_adapter.create_triple(triple)

    writer = mocked_adapter._local_item_engine(None)
    desc = 'Una persona' * 500
    shortened_desc = desc[:250] # 250 characters max
    set_desc_calls = [
        # first triple (desc_en)
        mock.call(shortened_desc, 'es'),
    ]
    writer.set_description.assert_has_calls(set_desc_calls, any_order=False)

def test_literal_datatype(mocked_adapter, triples):
    triple = triples['literal_datatype']
    mocked_adapter.create_triple(triple)
    item_engine_calls = [
        mock.call(new_item=True),
        mock.call(new_item=True),
        mock.call('Q1', data=[triple.object.to_wdi_datatype(prop_nr=triple.predicate.id)],
                  append_value=[triple.predicate.id])
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False)

def test_mappings_are_created_without_asio(mocked_adapter, triples):
    triple = triples['desc_en']
    res = mocked_adapter.create_triple(triple)
    assert mocked_adapter._add_mappings_to_entity.call_count == 1

def test_mappings_are_not_created_with_asio(mocked_adapter, triples):
    triple = triples['desc_asio']
    res = mocked_adapter.create_triple(triple)
    assert mocked_adapter._add_mappings_to_entity.call_count == 0

def test_modification_result_is_returned(mocked_adapter, triples):
    triple = triples['wditemid']
    res = mocked_adapter.create_triple(triple)
    assert isinstance(res, ModificationResult)
    assert res.successful
    assert res.message == ""

def test_proptype(mocked_adapter, triples):
    triple = triples['proptype']
    mocked_adapter.create_triple(triple)
    writer = mocked_adapter._local_item_engine(None)
    login = mocked_adapter._local_login
    write_calls = [
        mock.call(login, entity_type='property', property_datatype='wikibase-property'),
        mock.call(login)
    ]
    writer.write.assert_has_calls(write_calls, any_order=False)

def test_remove_triple(mocked_adapter, triples):
    triple = triples['wditemid']
    mocked_adapter.remove_triple(triple)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # create predicate
        mock.call(new_item=True),
        # remove statement
        mock.call('Q1', data=[wdi_core.WDBaseDataType.delete_statement('P2')])
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False)
    assert mocked_adapter._local_item_engine.call_count == 3

    writer = mocked_adapter._local_item_engine(None)
    login = mocked_adapter._local_login
    write_calls = [
        mock.call(login, entity_type='item', property_datatype=None),
        mock.call(login, entity_type='property', property_datatype='wikibase-item'),
        mock.call(login, entity_type='item', property_datatype='wikibase-item')
    ]
    writer.write.assert_has_calls(write_calls, any_order=False)

def test_remove_alias(mocked_adapter, triples):
    alias_es = triples['alias_es']
    alias_es_2 = triples['alias_es_2']
    mocked_adapter.create_triple(alias_es)
    mocked_adapter.create_triple(alias_es_2)
    mocked_adapter.remove_triple(alias_es)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # set alias for item Q1 (es)
        mock.call('Q1'),
        # set alias for item Q1 (es2)
        mock.call('Q1'),
        # remove alias for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls)

    writer = mocked_adapter._local_item_engine(None)
    set_alias_calls = [
        mock.call(['individuo'], 'es'),
        mock.call(['sujeto'], 'es'),
        mock.call(writer.get_aliases(), 'es', append=False)
    ]
    writer.set_aliases.assert_has_calls(set_alias_calls, any_order=False)

    get_alias_calls = [mock.call('es')]
    writer.get_aliases.assert_has_calls(get_alias_calls, any_order=False)

def test_remove_nonexisting_alias(mocked_adapter, triples, caplog):
    alias_es = triples['alias_es']
    mocked_adapter._local_item_engine(None).get_aliases.return_value = []
    with caplog.at_level(logging.WARNING):
        mocked_adapter.remove_triple(alias_es)

    item_engine_calls = [
        # create subject
        mock.call(new_item=True)
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls)

    writer = mocked_adapter._local_item_engine(None)
    set_alias_calls = []
    writer.set_aliases.assert_has_calls(set_alias_calls, any_order=False)

    get_alias_calls = [
        mock.call('es')
    ]
    writer.get_aliases.assert_has_calls(get_alias_calls, any_order=False)

    assert "Alias individuo@es does not exist" in caplog.text

def test_remove_description(mocked_adapter, triples):
    desc_es = triples['desc_es']
    mocked_adapter.create_triple(desc_es)
    mocked_adapter.remove_triple(desc_es)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # set description for item Q1
        mock.call('Q1'),
        # remove description for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls)

    writer = mocked_adapter._local_item_engine(None)
    set_desc_calls = [
        # create triple
        mock.call('Una persona', 'es'),
        # remove triple
        mock.call('', 'es')
    ]
    writer.set_description.assert_has_calls(set_desc_calls, any_order=False)

def test_remove_label(mocked_adapter, triples):
    label_en = triples['label_en']
    mocked_adapter.create_triple(label_en)
    mocked_adapter.remove_triple(label_en)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # create label for item Q1
        mock.call('Q1'),
        # remove label for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False)

    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        # default URI label
        mock.call('labra'),
        # label created with rdfs:label predicate
        mock.call('Jose Emilio Labra Gayo', 'en'),
        # removed label
        mock.call('', 'en')
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)

def test_set_alias(mocked_adapter, triples):
    alias_en = triples['alias_en']
    alias_es = triples['alias_es']
    mocked_adapter.create_triple(alias_en)
    mocked_adapter.create_triple(alias_es)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # set alias for item Q1
        mock.call('Q1'),
        # set alias again ('es') for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls)

    writer = mocked_adapter._local_item_engine(None)
    set_alias_calls = [
        # first triple (desc_en)
        mock.call(['individual'], 'en'),
        # second triple (desc_es)
        mock.call(['individuo'], 'es')
    ]
    writer.set_aliases.assert_has_calls(set_alias_calls, any_order=False)

def test_set_description(mocked_adapter, triples):
    desc_en = triples['desc_en']
    desc_es = triples['desc_es']
    mocked_adapter.create_triple(desc_en)
    mocked_adapter.create_triple(desc_es)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # set description for item Q1
        mock.call('Q1'),
        # set description again ('es') for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls)

    writer = mocked_adapter._local_item_engine(None)
    set_desc_calls = [
        # first triple (desc_en)
        mock.call('A person', 'en'),
        # second triple (desc_es)
        mock.call('Una persona', 'es')
    ]
    writer.set_description.assert_has_calls(set_desc_calls, any_order=False)

def test_set_label(mocked_adapter, triples):
    new_triple = triples['label_en']
    mocked_adapter.create_triple(new_triple)
    item_engine_calls = [
        # create subject
        mock.call(new_item=True),
        # create label for item Q1
        mock.call('Q1')
    ]
    mocked_adapter._local_item_engine.assert_has_calls(item_engine_calls, any_order=False)

    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        # default URI label
        mock.call('labra'),
        # label created with rdfs:label predicate
        mock.call('Jose Emilio Labra Gayo', 'en')
    ]
    writer.set_label.assert_has_calls(set_label_calls, any_order=False)

def test_unknown_language(mocked_adapter, triples, caplog):
    triple = triples['label_unknown']
    mock_error_msg = {
        'error': {
            'code': 'not-recognized-language',
            'info': 'The supplied language code was not recognized.',
            'messages': [],
            '*': ''
        }
    }
    writer = mocked_adapter._local_item_engine(None)
    writer.write = lambda x, **kwargs: raise_wdapierror(mock_error_msg)

    with caplog.at_level(logging.WARNING):
        modification_result = mocked_adapter.create_triple(triple)
    assert "Language was not recognized" in caplog.text
    assert not modification_result.successful
    assert modification_result.message == mock_error_msg['error']['info']

def test_utf_8(mocked_adapter, triples):
    triple_ko = triples['label_ko']
    mocked_adapter.create_triple(triple_ko)
    writer = mocked_adapter._local_item_engine(None)
    set_label_calls = [
        mock.call('labra'),
        mock.call('라브라', 'ko')
    ]
    writer.set_label.assert_has_calls(set_label_calls)
