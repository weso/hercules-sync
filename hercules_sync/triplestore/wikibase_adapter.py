from wikidataintegrator import wdi_core, wdi_login, wdi_helpers

from . import TripleInfo, TripleStoreManager, ModificationResult

class WikibaseAdapter(TripleStoreManager):

    def __init__(self, mediawiki_api_url, sparql_endpoint_url, username, password):
        self._local_item_engine = wdi_core.WDItemEngine. \
            wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
        # TODO: use OAuth
        self._local_login = wdi_login.WDLogin(username, password, mediawiki_api_url)

    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def modify_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass
