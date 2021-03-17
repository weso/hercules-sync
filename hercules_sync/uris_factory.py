import requests
import json
from wbsync.external import URIFactory


class HerculesURIsFactory(URIFactory):

    def get_uri(self, uriref) -> str:
        criteria = "concept="
        if(uriref.etype=='property'):
            criteria = "propery="
        criteria+=self.get_element(uriref.uri)
        response = requests.get("http://localhost:9326/canonical-uri?"+criteria+"&domain=hercules.org&subDomain=um&typeCode=res").content
        responseObj = json.loads(response)
        if (len(responseObj) > 0):
            return responseObj[0]["id"]
        return None

    def post_uri(self, uriref, wb_uri) -> None:
        criteria = "concept="
        if (uriref.etype == 'property'):
            criteria = "propery="
        criteria += self.get_element(uriref.uri)
        respone = requests.post(
            "http://localhost:9326/canonical-uri?"+criteria+"&domain=hercules.org&subDomain=um&typeCode=res").content
        responseObj = json.loads(respone)
        if (len(responseObj) > 0):
            return responseObj["id"]
        return None


    def get_element(self,uri:str) -> str:
        separator = uri.split("#")
        if (len(separator) == 2):
            return separator[1]
        else:
           separator = uri.split("/")
           return separator[len(separator) - 1]