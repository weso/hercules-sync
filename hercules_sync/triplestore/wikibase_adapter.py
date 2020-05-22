import json
import logging
import requests

from typing import Union

from wikidataintegrator import wdi_core, wdi_login

from . import TripleInfo, TripleStoreManager, ModificationResult, \
              TripleElement, URIElement, AnonymousElement
from ..external.uri_factory_mock import URIFactory
from ..util.uri_constants import RDFS_LABEL, RDFS_COMMENT, SCHEMA_NAME, \
              SCHEMA_DESCRIPTION, SKOS_ALTLABEL, SKOS_PREFLABEL

NonLiteralElement = Union[URIElement, AnonymousElement]

logger = logging.getLogger(__name__)

DEFAULT_LANG = 'es'
ERR_CODE_LANGUAGE = 'not-recognized-language'
MAPPINGS_PROP_LABEL = "same as"
MAPPINGS_PROP_DESC = "Mapping of an item to its original URI"
MAX_CHARACTERS_DESC = 250

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
        self.api_url = mediawiki_api_url
        self.sparql_url =  sparql_endpoint_url
        self._local_item_engine = wdi_core.WDItemEngine. \
            wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
        self._local_login = wdi_login.WDLogin(username, password, mediawiki_api_url)
        self._mappings_prop = self._get_or_create_mappings_prop()

    def create_triple(self, triple_info: TripleInfo) -> ModificationResult:
        """ Creates the given triple in the wikibase instance.

        Parameters
        ----------
        triple_info: :obj:`TripleInfo`
            Instance of the TripleInfo class with the data to be added to the wikibase.

        Returns
        -------
        :obj:`ModificationResult`
            ModificationResult object with the results of the operation.
        """
        logger.info(f"Create triple: {triple_info}")
        subject, predicate, objct = triple_info.content
        subject.id = self._get_wb_id_of(subject, subject.wdi_proptype)

        if self.is_wb_label(predicate):
            return self._set_label(subject, objct)

        if self.is_wb_description(predicate):
            return self._set_description(subject, objct)

        if self.is_wb_alias(predicate):
            return self._set_alias(subject, objct)

        if isinstance(objct, URIElement) or isinstance(objct, AnonymousElement):
            objct.id = self._get_wb_id_of(objct, objct.wdi_proptype)

        predicate.etype = 'property'
        predicate.id = self._get_wb_id_of(predicate, objct.wdi_dtype)

        return self._create_statement(subject, predicate, objct)

    def remove_triple(self, triple_info: TripleInfo) -> ModificationResult:
        """ Removes the given triple from the wikibase instance.

        Parameters
        ----------
        triple_info: :obj:`TripleInfo`
            Instance of the TripleInfo class with the data to be removed from the wikibase.

        Returns
        -------
        :obj:`ModificationResult`
            ModificationResult object with the results of the operation.
        """
        logger.info(f"Remove triple: {triple_info}")
        subject, predicate, objct = triple_info.content
        subject.id = self._get_wb_id_of(subject, subject.wdi_proptype)

        if self.is_wb_label(predicate):
            return self._remove_label(subject, objct)

        if self.is_wb_description(predicate):
            return self._remove_description(subject, objct)

        if self.is_wb_alias(predicate):
            return self._remove_alias(subject, objct)

        predicate.etype = 'property'
        predicate.id = self._get_wb_id_of(predicate, objct.wdi_dtype)
        return self._remove_statement(subject, predicate)

    def _create_statement(self, subject: TripleElement, predicate: TripleElement,
                          objct: TripleElement) -> ModificationResult:
        statement = objct.to_wdi_datatype(prop_nr=predicate.id)
        data = [statement]
        litem = self._local_item_engine(subject.id, data=data, append_value=[predicate.id])
        return self._try_write(litem, entity_type=subject.etype,
                               property_datatype=subject.wdi_dtype)

    def _remove_statement(self, subject: TripleElement,
                          predicate: TripleElement) -> ModificationResult:
        statement_to_remove = wdi_core.WDBaseDataType.delete_statement(predicate.id)
        data = [statement_to_remove]
        litem = self._local_item_engine(subject.id, data=data)
        return self._try_write(litem, entity_type=subject.etype,
                               property_datatype=subject.wdi_dtype)

    def _add_mappings_to_entity(self, entity, uri: str):
        same_as = wdi_core.WDUrl(value=uri, prop_nr=self._mappings_prop)
        entity.update([same_as], append_value=[self._mappings_prop])

    def _create_new_wb_item(self, uriref: NonLiteralElement, proptype: str) -> ModificationResult:
        entity = self._local_item_engine(new_item=True)
        label = try_infer_label_from(uriref)
        if label is None:
            logging.warning("Label for URI %s could not be inferred.", uriref)
        else:
            entity.set_label(label)

        if not is_asio_uri(uriref):
            self._add_mappings_to_entity(entity, uriref.uri)

        return self._try_write(entity, entity_type=uriref.etype,
                               property_datatype=proptype)

    def _get_or_create_mappings_prop(self):
        mappings_prop_id = None
        query_res = json.loads(requests.get(f"{self.api_url}?action=wbsearchentities" + \
            f"&search={MAPPINGS_PROP_LABEL}&format=json&language=en&type=property").text)
        if 'search' in query_res and len(query_res['search']) > 0:
            for search_result in query_res['search']:
                if search_result['label'] == MAPPINGS_PROP_LABEL and \
                   search_result['description'] == MAPPINGS_PROP_DESC:
                    mappings_prop_id = search_result['id']
                    logger.info("Mappings property has been found: %s", mappings_prop_id)
                    break

        if mappings_prop_id is None:
            logger.info("Mappings property was not found in the wikibase. Creating it...")
            mappings_item = self._local_item_engine(new_item=True)
            mappings_item.set_label(MAPPINGS_PROP_LABEL, lang='en')
            mappings_item.set_description(MAPPINGS_PROP_DESC, lang='en')
            mappings_prop_id = mappings_item.write(self._local_login, entity_type='property',
                                                   property_datatype='url')
            logger.info("Mappings property has been created: %s", mappings_prop_id)
        return mappings_prop_id

    def _get_wb_id_of(self, uriref: NonLiteralElement, proptype: str):
        wb_uri = get_uri_for(uriref.uri)
        if wb_uri is not None:
            logging.debug("Id of %s in wikibase: %s", uriref, wb_uri)
            return wb_uri

        logging.debug("Entity %s doesn't exist in wikibase. Creating it...", uriref)
        modification_result = self._create_new_wb_item(uriref, proptype)
        entity_id = modification_result.result

        # update uri factory with new item
        post_uri(uriref.uri, entity_id)
        return entity_id

    def _set_alias(self, subject, objct) -> ModificationResult:
        lang = get_lang_from_literal(objct)
        logging.debug("Changing alias @%s of %s", lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_aliases([objct.content], lang)
        return self._try_write(entity, entity_type=subject.etype)

    def _set_label(self, subject, objct) -> ModificationResult:
        lang = get_lang_from_literal(objct)
        logging.debug("Changing label @%s of %s", lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_label(objct.content, lang)
        return self._try_write(entity, entity_type=subject.etype)

    def _set_description(self, subject, objct) -> ModificationResult:
        lang = get_lang_from_literal(objct)
        logging.debug("Setting description @%s of %s", lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_description(objct.content[:MAX_CHARACTERS_DESC], lang)
        return self._try_write(entity, entity_type=subject.etype)

    def _remove_alias(self, subject, objct) -> ModificationResult:
        lang = get_lang_from_literal(objct)
        logging.debug("Removing alias @%s of %s", lang, subject)
        entity = self._local_item_engine(subject.id)
        curr_aliases = entity.get_aliases(lang)
        try:
            curr_aliases.remove(objct.content)
        except ValueError:
            logging.warning("Alias %s@%s does not exist for object %s. Skipping removal...",
                            objct.content, lang, subject.id)
            err_msg = f"Error removing alias {objct.content}@{lang}."
            return ModificationResult(successful=False, message=err_msg)
        entity.set_aliases(curr_aliases, lang, append=False)
        return self._try_write(entity, entity_type=subject.etype)


    def _remove_label(self, subject, objct) -> ModificationResult:
        lang = get_lang_from_literal(objct)
        logging.debug("Removing label @%s of %s", lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_label("", lang)
        return self._try_write(entity, entity_type=subject.etype)

    def _remove_description(self, subject, objct) -> ModificationResult:
        lang = get_lang_from_literal(objct)
        logging.debug("Removing description @%s of %s", lang, subject)
        entity = self._local_item_engine(subject.id)
        entity.set_description("", lang)
        return self._try_write(entity, entity_type=subject.etype)

    def _try_write(self, entity, **kwargs) -> ModificationResult:
        try:
            eid = entity.write(self._local_login, **kwargs)
            return ModificationResult(successful=True, res=eid)
        except wdi_core.WDApiError as err:
            logger.warning(err.wd_error_msg['error'])
            err_code = err.wd_error_msg['error']['code']
            msg = err.wd_error_msg['error']['info']
            if err_code == ERR_CODE_LANGUAGE:
                logger.warning("Language was not recognized. Skipping it...")
            return ModificationResult(successful=False, message=msg)

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

def get_lang_from_literal(objct):
    if not hasattr(objct, 'lang') or objct.lang is None:
        logging.warning("Literal %s has no language. Defaulting to '%s'", objct, DEFAULT_LANG)
        return DEFAULT_LANG
    return objct.lang

def is_asio_uri(uriref: NonLiteralElement) -> bool:
    return '/hercules/asio' in uriref.uri

def post_uri(label, uri):
    logging.debug("Calling POST of URIFactory: %s - %s", label, uri)
    uri_factory = URIFactory()
    return uri_factory.post_uri(label, uri)

def try_infer_label_from(uriref: NonLiteralElement):
    if '#' in uriref:
        return uriref.uri.split('#')[-1]
    elif '/' in uriref:
        return uriref.uri.split('/')[-1]
    else:
        return None
