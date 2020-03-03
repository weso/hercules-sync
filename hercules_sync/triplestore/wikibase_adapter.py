from . import TripleInfo, TripleStoreManager, ModificationResult

class WikibaseAdapter(TripleStoreManager):

    def __init__(self, endpoint, username, password):
        pass

    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def modify_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass
