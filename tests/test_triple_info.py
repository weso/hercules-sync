import pytest

from rdflib.term import Literal, URIRef
from rdflib.namespace import XSD
from wikidataintegrator.wdi_core import WDItemID, WDProperty, WDString, WDQuantity, WDMonolingualText

from hercules_sync.triplestore import LiteralElement, TripleElement, TripleInfo, URIElement
from hercules_sync.util.error import InvalidArgumentError
from hercules_sync.util.uri_constants import GEO_BASE

@pytest.fixture()
def rdflib_triple():
    return (URIRef('http://example.org/onto#Human'),
            URIRef('http://example.org/onto#altName'),
            Literal('Person'))

@pytest.fixture
def prop_uri():
    uri = 'http://example.org/onto#livesIn'
    etype = 'property'
    return URIElement(uri, etype)

@pytest.fixture
def item_uri():
    uri = 'http://example.org/onto#Person'
    return URIElement(uri)

@pytest.fixture
def string_literal():
    return LiteralElement('test')

@pytest.fixture
def monolingual_literal():
    return LiteralElement('목소리', lang='ko')

@pytest.fixture
def datatype_literal():
    return LiteralElement("12", datatype=XSD.integer)

def test_from_rdflib(rdflib_triple):
    triple = TripleInfo.from_rdflib(rdflib_triple).content
    assert isinstance(triple[0], URIElement)
    assert isinstance(triple[1], URIElement)
    assert isinstance(triple[2], LiteralElement)

    assert triple[0].uri == str(rdflib_triple[0])
    assert triple[1].uri == str(rdflib_triple[1])
    assert triple[2].content == rdflib_triple[2].value
    assert triple[2].datatype is None
    assert triple[2].lang is None

def test_is_uri(string_literal, item_uri):
    assert not string_literal.is_uri()
    assert item_uri.is_uri()

def test_literal_init():
    lit_a = LiteralElement("hello")
    assert lit_a.content == "hello"
    assert lit_a.datatype is None
    assert lit_a.lang is None

    lit_b = LiteralElement("hello again", lang='en')
    assert lit_b.content == "hello again"
    assert lit_b.lang == "en"
    assert lit_b.datatype is None

    lit_c = LiteralElement("12", datatype=XSD.integer)
    assert lit_c.content == "12"
    assert lit_c.datatype == XSD.integer
    assert lit_c.lang is None

    with pytest.raises(InvalidArgumentError) as excpt:
        LiteralElement("12", datatype=XSD.integer, lang='es')
    assert 'Both datatype and language' in str(excpt.value)

def test_literal_str(string_literal, monolingual_literal, datatype_literal):
    assert str(string_literal) == 'LiteralElement: test'
    assert str(monolingual_literal) == 'LiteralElement: 목소리 - Language: ko'
    assert str(datatype_literal) == f'LiteralElement: 12 - DataType: {XSD.integer}'

def test_literal_wdi_class(string_literal, monolingual_literal, datatype_literal):
    assert string_literal.wdi_class == WDString
    assert monolingual_literal.wdi_class == WDMonolingualText
    assert datatype_literal.wdi_class == WDQuantity

def test_literal_wdi_dtype(string_literal, monolingual_literal, datatype_literal):
    assert string_literal.wdi_dtype == WDString.DTYPE
    assert monolingual_literal.wdi_dtype == WDMonolingualText.DTYPE
    assert datatype_literal.wdi_dtype == WDQuantity.DTYPE

def test_literal_equals(string_literal, monolingual_literal, datatype_literal):
    assert 'test' != string_literal
    assert LiteralElement('test') == string_literal
    assert LiteralElement('목소리', lang='ko') == monolingual_literal
    assert LiteralElement('12', datatype=XSD.integer) == datatype_literal

def test_uri_init(prop_uri):
    assert prop_uri.uri == 'http://example.org/onto#livesIn'
    assert prop_uri.etype == 'property'
    assert prop_uri.id is None
    assert prop_uri.proptype is None

def test_uri_etype():
    element = URIElement('')
    assert element.etype == 'item'

    element.etype = 'property'
    assert element.etype == 'property'

    with pytest.raises(InvalidArgumentError) as excpt:
        element.etype = 'invented'
    assert 'Invalid etype' in str(excpt.value)

def test_uri_str(item_uri):
    expected = f"URIElement: {item_uri.uri} - Type: item"
    assert expected == str(item_uri)

def test_uri_wdi_class(prop_uri, item_uri):
    assert prop_uri.wdi_class == WDProperty
    assert item_uri.wdi_class == WDItemID

def test_uri_wdi_dtype(prop_uri, item_uri):
    assert prop_uri.wdi_dtype == WDProperty.DTYPE
    assert item_uri.wdi_dtype == WDItemID.DTYPE

def test_uri_wdi_proptype(prop_uri, item_uri):
    assert prop_uri.wdi_proptype is None
    assert item_uri.wdi_proptype is None

    prop_uri.proptype = 'invented'
    assert prop_uri.wdi_proptype is None

    prop_uri.proptype = f'{GEO_BASE}wktLiteral'
    item_uri.proptype = f'{GEO_BASE}wktLiteral'
    assert prop_uri.wdi_proptype == 'globe-coordinate'
    assert item_uri.wdi_proptype is None
