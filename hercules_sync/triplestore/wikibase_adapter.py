from wikidataintegrator import wdi_core, wdi_login, wdi_helpers

from . import TripleInfo, TripleStoreManager, ModificationResult

from ..external.uri_factory_mock import URIFactory

class WikibaseAdapter(TripleStoreManager):

    def __init__(self, mediawiki_api_url, sparql_endpoint_url, username, password):
        self._local_item_engine = wdi_core.WDItemEngine. \
            wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
        # TODO: use OAuth
        self._local_login = wdi_login.WDLogin(username, password, mediawiki_api_url)

    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        # TODO: parse special case of labels and comments
        if triple_info.predicate == 'http://www.w3.org/2000/01/rdf-schema#label':
            pass

        # TODO: parse property datatype from Python type of property in triple_info
        prop_id = self._get_wb_id_of(triple_info.predicate, 'property', 'wikibase-item')
        subject_id = self._get_wb_id_of(triple_info.subject, 'item')
        object_id = self._get_wb_id_of(triple_info.object, 'item')

        statement = wdi_core.WDItemID(value=object_id, prop_nr=prop_id)
        data = [statement]
        litem = self._local_item_engine(subject_id, data=data)
        litem.write(self._local_login)

    def modify_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def _get_wb_id_of(self, uriref, entity_type, property_datatype='string'):
        wb_uri = get_uri_for(uriref)
        if wb_uri is not None:
            return wb_uri

        entity = self._local_item_engine(new_item=True)
        entity_id = entity.write(self._local_login, entity_type=entity_type,
                                 property_datatype=property_datatype)

        # update uri factory with new item
        post_uri(uriref, entity_id)

        return entity_id

def get_uri_for(label):
    uri_factory = URIFactory()
    return uri_factory.get_uri(label)

def post_uri(label, uri):
    uri_factory = URIFactory()
    return uri_factory.post_uri(label, uri)
