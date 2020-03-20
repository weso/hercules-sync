from rdflib.term import Literal, URIRef
from rdflib.namespace import XSD

def literal2element(literal):
    """ Converts a rdflib literal to a triple element.

    Parameters
    ----------
    literal : :obj:`rdflib.term.Literal`

    Returns
    -------
    :obj:`herc_sync.triplestore.TripleElement`

    """
    if (hasattr(literal, 'lang')):
        pass

def uriref2wbitem(element):
    pass

def literal2wbitem():
    pass
