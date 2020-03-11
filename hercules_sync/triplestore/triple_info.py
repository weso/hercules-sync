
class TripleInfo():
    def __init__(self, sub, pred, obj):
        self.subject = sub
        self.predicate = pred
        self.object = obj

    @classmethod
    def from_rdflib(cls, rdflib_triple):
        subject = TripleElement.from_rdflib(rdflib_triple[0])
        predicate = TripleElement.from_rdflib(rdflib_triple[1])
        objct = TripleElement.from_rdflib(rdflib_triple[2])
        return TripleInfo(subject, predicate, objct)

class TripleElement():
    @classmethod
    def from_rdflib(cls, rdflib_element):
        pass

class URIElement(TripleElement):
    def __init__(self, uri):
        pass

class LiteralElement(TripleElement):
    def __init__(self, content, datatype):
        pass
