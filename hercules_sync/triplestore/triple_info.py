from rdflib.term import Literal, URIRef

from abc import abstractmethod, ABC

from ..util import mappings

class TripleElement(ABC):
    @classmethod
    def from_rdflib(cls, rdflib_element):
        elmnt_type = type(rdflib_element)
        res = None
        if elmnt_type == URIRef:
            res = URIElement(rdflib_element.uri)
        elif elmnt_type == Literal:
            res = LiteralElement(rdflib_element.value, rdflib_element.datatype,
                                 rdflib_element.language)
        return res

    @abstractmethod
    def to_wdi_datatype(self):
        pass

    def __str__(self):
        pass

class URIElement(TripleElement):
    VALID_ETYPES = ['item', 'property']

    def __init__(self, uri: str, etype='item'):
        self.uri = uri
        self.etype = etype
        if etype not in self.VALID_ETYPES:
            raise SomeError('Invalid etype received, valid values are: ', self.VALID_ETYPES)

    @property
    def wdi_dtype(self):
        return 'wikibase-item'

    def to_wdi_datatype(self) -> WDBaseDataType:
        if self.etype == 'item':
            return WDItemID
        elif self.etype == 'property':
            return WDProperty

class LiteralElement(TripleElement):
    def __init__(self, content, datatype=None, lang=None):
        self.content = content
        if datatype and lang:
            raise SomeError("Both datatype and language can't be set.")
        self.datatype = datatype
        self.lang = lang

    @property
    def wdi_dtype(self):
        return 'wikibase-item'

    def to_wdi_datatype(self):
        if self.lang:
            return WDMonolingual
        elif self.datatype:
            ...
        else:
            return WDString

    def wb_datatype(self):
        pass

class TripleInfo():
    def __init__(self, sub: TripleElement, pred: TripleElement, obj: TripleElement):
        self.subject = sub
        self.predicate = pred
        self.object = obj

    @classmethod
    def from_rdflib(cls, rdflib_triple):
        subject = TripleElement.from_rdflib(rdflib_triple[0])
        predicate = TripleElement.from_rdflib(rdflib_triple[1])
        objct = TripleElement.from_rdflib(rdflib_triple[2])
        return TripleInfo(subject, predicate, objct)
