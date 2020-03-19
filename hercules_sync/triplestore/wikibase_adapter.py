import logging

from wikidataintegrator import wdi_core, wdi_login, wdi_helpers

from . import TripleInfo, TripleStoreManager, ModificationResult
from ..external.uri_factory_mock import URIFactory
from ..util.uri_constants import RDFS_LABEL, RDFS_COMMENT

logger = logging.getLogger(__name__)

class WikibaseAdapter(TripleStoreManager):

    def __init__(self, mediawiki_api_url, sparql_endpoint_url, username, password):
        self._local_item_engine = wdi_core.WDItemEngine. \
            wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
        self._local_login = wdi_login.WDLogin(username, password, mediawiki_api_url)

    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        # TODO: When the basic ontology reasoner is implemented, infer is subject and object
        # are either items or properties
        subject_id = self._get_wb_id_of(triple_info.subject, 'item')

        if triple_info.predicate == RDFS_LABEL:
            self._set_label(triple_info.subject, subject_id, triple_info.object)
            return

        if triple_info.predicate == RDFS_COMMENT:
            self._set_description(triple_info.subject, subject_id, triple_info.object)
            return

        object_id = self._get_wb_id_of(triple_info.object, 'item')

        # TODO: parse property datatype from Python type of property in triple_info
        prop_id = self._get_wb_id_of(triple_info.predicate, 'property', 'wikibase-item')

        self._create_statement(subject_id, prop_id, object_id)

    def modify_triple(self, triple_info: TripleInfo) -> ModificationResult:
        pass

    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        subject_id = self._get_wb_id_of(triple_info.subject, 'item')

        if triple_info.predicate == RDFS_LABEL:
            self._remove_label(triple_info.subject, subject_id, triple_info.object)
            return

        if triple_info.predicate == RDFS_COMMENT:
            self._remove_description(triple_info.subject, subject_id, triple_info.object)
            return

        prop_id = self._get_wb_id_of(triple_info.predicate, 'property', 'wikibase-item')
        self._remove_statement(subject_id, prop_id)

    def _create_statement(self, subject_id, prop_id, object_id):
        statement = wdi_core.WDItemID(value=object_id, prop_nr=prop_id)
        data = [statement]
        litem = self._local_item_engine(subject_id, data=data)
        litem.write(self._local_login)

    def _remove_statement(self, subject_id, prop_id):
        statement_to_remove = wdi_core.WDItemID.delete_statement(prop_id)
        data = [statement_to_remove]
        litem = self._local_item_engine(subject_id, data=data)
        litem.write(self._local_login)

    def _get_wb_id_of(self, uriref, entity_type, property_datatype='string'):
        wb_uri = get_uri_for(uriref)
        if wb_uri is not None:
            logging.debug("Id of %s in wikibase: %s", uriref, wb_uri)
            return wb_uri

        logging.debug("Entity %s doesn't exist in wikibase. Creating it...", uriref)
        entity_id = self._create_new_wb_item(uriref, entity_type, property_datatype)

        # update uri factory with new item
        post_uri(uriref, entity_id)
        return entity_id

    def _create_new_wb_item(self, uriref, entity_type, property_datatype):
        entity = self._local_item_engine(new_item=True)
        if '#' not in uriref:
            logging.warning("URI %s doesn't contain a '#' separator. Default "
                            "label can't be inferred.", uriref)
        else:
            label = uriref.split("#")[-1]
            entity.set_label(label)
        entity_id = entity.write(self._local_login, entity_type=entity_type,
                                 property_datatype=property_datatype)
        return entity_id

    def _set_label(self, subject, subject_id, objct):
        assert isinstance(objct, LanguageLiteral)
        logging.debug("Changing label @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject_id)
        entity.set_label(objct.val, objct.lang)

    def _set_description(self, subject, subject_id, objct):
        logging.debug("Removing description @%s of %s", obct.lang, subject)
        entity = self._local_item_engine(subject_id)
        entity.set_description(objct.val, objct.lang)

    def _remove_label(self, subject, subject_id, objct):
        assert isinstance(objct, LanguageLiteral)
        logging.debug("Removing label @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject_id)
        entity.set_label("", objct.lang)

    def _remove_description(self, subject, subject_id, objct):
        logging.debug("Removing description @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject_id)
        entity.set_description("", objct.lang)


def get_uri_for(label):
    uri_factory = URIFactory()
    return uri_factory.get_uri(label)

def post_uri(label, uri):
    logging.debug("Calling POST of URIFactory: %s - %s", label, uri)
    uri_factory = URIFactory()
    return uri_factory.post_uri(label, uri)
