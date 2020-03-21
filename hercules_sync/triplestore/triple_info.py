from rdflib.term import Literal, URIRef
from wikidataintegrator.wdi_core import WDBaseDataType, WDItemID, WDMonolingualText, \
                                        WDProperty, WDString

from abc import abstractmethod, ABC
from functools import partial
from typing import Type, Union

from ..util.error import InvalidArgumentError

class TripleElement(ABC):
    @classmethod
    def from_rdflib(cls, rdflib_element):
        elmnt_type = type(rdflib_element)
        res = None
        if elmnt_type == URIRef:
            res = URIElement(str(rdflib_element))
        elif elmnt_type == Literal:
            res = LiteralElement(rdflib_element.value, rdflib_element.datatype,
                                 rdflib_element.language)
        return res

    @abstractmethod
    def to_wdi_datatype(self, **kwargs):
        pass

class URIElement(TripleElement):
    VALID_ETYPES = ['item', 'property']

    def __init__(self, uri: str, etype='item'):
        self.uri = uri
        self.etype = etype
        self.id = None

    @property
    def etype(self):
        return self._etype

    @etype.setter
    def etype(self, new_val: str) -> str:
        """
        """
        if new_val not in self.VALID_ETYPES:
            raise InvalidArgumentError('Invalid etype received, valid values are: ',
                                       self.VALID_ETYPES)
        self._etype = new_val
        return self._etype

    @property
    def wdi_class(self) -> Union[Type[WDItemID], Type[WDProperty]]:
        """ Returns the wikidataintegrator class of the element
        """
        assert self.etype in self.VALID_ETYPES
        return WDItemID if self.etype == 'item' else WDProperty

    @property
    def wdi_dtype(self) -> str:
        """ Returns the wikidataintegrator DTYPE of this element.
        """
        return self.wdi_class.DTYPE

    def to_wdi_datatype(self, **kwargs) -> Union[WDItemID, WDProperty]:
        """ Returns an instance of the wdi_core class of this element
        """
        return self.wdi_class(value=self.id, **kwargs)

    def __eq__(self, val):
        return self.uri == val

    def __iter__(self):
        return self.uri.__iter__()

    def __str__(self):
        return f"URIElement: {self.uri} - Type: {self.etype}"

class LiteralElement(TripleElement):
    def __init__(self, content, datatype=None, lang=None):
        self.content = content
        if datatype and lang:
            raise InvalidArgumentError("Both datatype and language can't be set.")
        self.datatype = datatype
        self.lang = lang

    @property
    def wdi_class(self) -> Type[WDBaseDataType]:
        if self.lang:
            return WDMonolingualText
        elif self.datatype:
            raise NotImplementedError("Use of xsd:schema datatypes is not implemented yet.")
        else:
            return WDString

    @property
    def wdi_dtype(self) -> str:
        return self.wdi_class.DTYPE

    def to_wdi_datatype(self, **kwargs) -> WDBaseDataType:
        if self.lang:
            return self.wdi_class(value=self.content, language=self.lang, *kwargs)
        elif self.datatype:
            raise NotImplementedError("Use of xsd:schema datatypes is not implemented yet.")
        else:
            return self.wdi_class(value=self.content, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, LiteralElement):
            return False
        return self.content == other.content and self.lang == other.lang \
               and self.datatype == other.datatype

    def __str__(self):
        res = [f"LiteralElement: {self.content}"]
        if self.lang:
            res.append(f" - Language: {self.lang}")
        if self.datatype:
            res.append(f" - DataType: {self.datatype}")
        return ''.join(res)

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

    @property
    def content(self):
        return (self.subject, self.predicate, self.object)

    def __eq__(self, other):
        if not isinstance(other, TripleInfo):
            return False

        return self.subject == other.subject and self.predicate == other.predicate \
               and self.object == other.object
