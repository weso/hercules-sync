import logging

from wikidataintegrator import wdi_core, wdi_login

from . import TripleInfo, TripleStoreManager, ModificationResult, \
              TripleElement, URIElement
from ..external.uri_factory_mock import URIFactory
from ..util.uri_constants import RDFS_LABEL, RDFS_COMMENT, SCHEMA_NAME, \
              SCHEMA_DESCRIPTION, SKOS_ALTLABEL, SKOS_PREFLABEL

logger = logging.getLogger(__name__)

class WikibaseAdapter(TripleStoreManager):
    """ Adapter to execute operations on a wikibase instance.

    Parameters
    ----------
    mediawiki_api_url : str
        String with the url where the mediawiki API is accesible.

    sparql_endpoint_url : str
        String with the url where the SPARQL endpoint of the instance is available.

    username : str
        Username of the account that is going to execute the operations.

    password : str
        Password of the account.
    """

    def __init__(self, mediawiki_api_url, sparql_endpoint_url, username, password):
        self._local_item_engine = wdi_core.WDItemEngine. \
            wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
        self._local_login = wdi_login.WDLogin(username, password, mediawiki_api_url)

    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        subject, predicate, objct = triple_info.content
        subject.id = self._get_wb_id_of(subject, subject.wdi_proptype)

        if self.is_wb_label(predicate):
            self._set_label(subject, objct)
            return

        if self.is_wb_description(predicate):
            self._set_description(subject, objct)
            return

        if self.is_wb_alias(predicate):
            self._set_alias(subject, objct)
            return

        if isinstance(objct, URIElement):
            objct.id = self._get_wb_id_of(objct, objct.wdi_proptype)

        predicate.etype = 'property'
        predicate.id = self._get_wb_id_of(predicate, objct.wdi_dtype)

        self._create_statement(subject, predicate, objct)

    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        subject, predicate, objct = triple_info.content
        subject.id = self._get_wb_id_of(subject, subject.wdi_proptype)

        if self.is_wb_label(predicate):
            self._remove_label(subject, objct)
            return

        if self.is_wb_description(predicate):
            self._remove_description(subject, objct)
            return

        if self.is_wb_alias(predicate):
            self._remove_alias(subject, objct)
            return

        predicate.etype = 'property'
        predicate.id = self._get_wb_id_of(predicate, objct.wdi_dtype)
        self._remove_statement(subject, predicate)

    def _create_statement(self, subject: TripleElement, predicate: TripleElement,
                          objct: TripleElement):
        statement = objct.to_wdi_datatype(prop_nr=predicate.id)
        data = [statement]
        litem = self._local_item_engine(subject.id, data=data, append_value=[predicate.id])
        litem.write(self._local_login, entity_type=subject.etype, property_datatype=subject.wdi_dtype)

    def _remove_statement(self, subject: TripleElement, predicate: TripleElement):
        statement_to_remove = wdi_core.WDBaseDataType.delete_statement(predicate.id)
        data = [statement_to_remove]
        litem = self._local_item_engine(subject.id, data=data)
        litem.write(self._local_login, entity_type=subject.etype, property_datatype=subject.wdi_dtype)

    def _get_wb_id_of(self, uriref: URIElement, proptype: str):
        wb_uri = get_uri_for(uriref.uri)
        if wb_uri is not None:
            logging.debug("Id of %s in wikibase: %s", uriref, wb_uri)
            return wb_uri

        logging.debug("Entity %s doesn't exist in wikibase. Creating it...", uriref)
        entity_id = self._create_new_wb_item(uriref, proptype)

        # update uri factory with new item
        post_uri(uriref.uri, entity_id)
        return entity_id

    def _create_new_wb_item(self, uriref: URIElement, proptype: str):
        entity = self._local_item_engine(new_item=True)
        if '#' not in uriref:
            logging.warning("URI %s doesn't contain a '#' separator. Default "
                            "label can't be inferred.", uriref)
        else:
            label = uriref.uri.split("#")[-1]
            entity.set_label(label)
        entity_id = entity.write(self._local_login, entity_type=uriref.etype,
                                 property_datatype=proptype)
        return entity_id

    def _set_alias(self, subject, objct):
        assert hasattr(objct, 'lang')
        logging.debug("Changing alias @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_aliases([objct.content], objct.lang)
        entity.write(self._local_login)

    def _set_label(self, subject, objct):
        assert hasattr(objct, 'lang')
        logging.debug("Changing label @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_label(objct.content, objct.lang)
        entity.write(self._local_login)

    def _set_description(self, subject, objct):
        logging.debug("Removing description @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_description(objct.content, objct.lang)
        entity.write(self._local_login)

    def _remove_alias(self, subject, objct):
        assert hasattr(objct, 'lang')
        logging.debug("Removing alias @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject.id)
        curr_aliases = entity.get_aliases(objct.lang)
        try:
            curr_aliases.remove(objct.content)
            entity.set_aliases(curr_aliases, objct.lang, append=False)
            entity.write(self._local_login)
        except ValueError:
            logging.warning("Alias %s@%s does not exist for object %s. Skipping removal...",
                            objct.content, objct.lang, subject.id)

    def _remove_label(self, subject, objct):
        assert hasattr(objct, 'lang')
        logging.debug("Removing label @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_label("", objct.lang)
        entity.write(self._local_login)

    def _remove_description(self, subject, objct):
        logging.debug("Removing description @%s of %s", objct.lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_description("", objct.lang)
        entity.write(self._local_login)

    @classmethod
    def is_wb_alias(cls, predicate: URIElement) -> bool:
        """ Returns whether the predicate corresponds to an alias in wikibase. """
        return predicate == SKOS_ALTLABEL

    @classmethod
    def is_wb_description(cls, predicate: URIElement) -> bool:
        """ Returns whether the predicate corresponds to a description in wikibase. """
        return predicate in [RDFS_COMMENT, SCHEMA_DESCRIPTION]

    @classmethod
    def is_wb_label(cls, predicate: URIElement) -> bool:
        """ Returns whether the predicate corresponds to a label in wikibase. """
        return predicate in [RDFS_LABEL, SKOS_PREFLABEL, SCHEMA_NAME]


def get_uri_for(label):
    uri_factory = URIFactory()
    return uri_factory.get_uri(label)

def post_uri(label, uri):
    logging.debug("Calling POST of URIFactory: %s - %s", label, uri)
    uri_factory = URIFactory()
    return uri_factory.post_uri(label, uri)
