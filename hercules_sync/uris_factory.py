import requests
import json
import logging
from wbsync.external import URIFactory

from config import _try_get_config_from_env

LOGGER = logging.getLogger(__name__)
URIS_FACTORY = _try_get_config_from_env('URIS_FACTORY')
WBAPI = _try_get_config_from_env('WBAPI').split("w/api.php")[0]

class HerculesURIsFactory(URIFactory):

    def get_uri(self, uriref) -> str:
        uri = self.get_element(uriref.uri)
        criteria = "entity"
        idSplit = "Item:"
        canonicalParams = {'domain': 'hercules.org', 'lang': 'es-ES', 'subDomain': 'um', 'type': 'res'}
        body = '{"@class": "'+uri+'","canonicalClassName": "'+uri+'" }'
        if(uriref.etype=='property'):
            criteria = "property"
            idSplit = "Property:"
            body = '{"property": "' + uri + '","canonicalProperty": "' + uri + '" }'

        canonicalResponse = requests.post(URIS_FACTORY+"uri-factory/canonical/" + criteria,
                                          params=canonicalParams,
                                          headers={'Content-type': 'application/json', 'Accept': '*/*'},
                                          data=body).content

        canonicalResponseObj = json.loads(canonicalResponse)
        canonicalUri = canonicalResponseObj["canonicalURI"]
        language = canonicalResponseObj["language"]

        localParams = {'canonicalUri': canonicalUri, 'languageCode': language, 'storageName': 'wikibase'}
        localResponse = requests.get(URIS_FACTORY+"uri-factory/local/canonical", params=localParams).content
        localResponseObj = json.loads(localResponse)


        if (len(localResponseObj) == 0):
            LOGGER.info("Local uri not found for: " + uri)
            return None


        localUri = localResponseObj[0]["localUri"].split(idSplit)[1]
        LOGGER.info("Local uri found for: " + uri + ": " +localUri)
        return localUri


    def post_uri(self, uriref, wb_uri) -> None:
        uri = self.get_element(uriref.uri)
        LOGGER.info("Creating a new local uri for: " + uri)
        criteria = "entity"
        idSplit = "Item:"
        canonicalParams = {'domain': 'hercules.org', 'lang': 'es-ES', 'subDomain': 'um', 'type': 'res'}
        body = '{"@class": "' + uri + '","canonicalClassName": "' + uri + '" }'
        if (uriref.etype == 'property'):
            criteria = "property"
            idSplit = "Property:"
            body = '{"property": "' + uri + '","canonicalProperty": "' + uri + '" }'

        canonicalResponse = requests.post(URIS_FACTORY + "uri-factory/canonical/" + criteria,
                                          params=canonicalParams,
                                          headers={'Content-type': 'application/json', 'Accept': '*/*'},
                                          data=body).content

        canonicalResponseObj = json.loads(canonicalResponse)
        canonicalLanguageURI = canonicalResponseObj["canonicalLanguageURI"]

        localParams = {'canonicalLanguageURI': canonicalLanguageURI, 'localURI': WBAPI+'wiki/'+idSplit+wb_uri,
                       'storageName': 'wikibase'}

        requests.post(URIS_FACTORY+"uri-factory/local", params=localParams).content
        LOGGER.info("Created a new local uri found for: " + uri )
        return wb_uri


    def get_element(self,uri:str) -> str:
        separator = uri.split("#")
        if (len(separator) == 2):
            return separator[1]
        else:
           separator = uri.split("/")
           return separator[len(separator) - 1]

