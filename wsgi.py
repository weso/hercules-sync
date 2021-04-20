""" Entry point of the hercules_sync server.
"""

from hercules_sync import create_app

import logging


logging.basicConfig(level=logging.INFO)

app = create_app()


if __name__ == '__main__':
    if app.config['ENV'] == 'production':
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0')

"""
            import requests
            import json

            criteria = "entity"
            canonicalParams = {'domain': 'hercules.org', 'lang': 'es-ES', 'subDomain':'um','type':'res'}
            body = '{"@class": "researcher","canonicalClassName": "researcher" }'
            canonicalResponse = requests.post("http://localhost:9326/uri-factory/canonical/"+criteria,params=canonicalParams,headers={'Content-type':'application/json', 'Accept':'*/*'},data=body).content
            canonicalResponseObj = json.loads(canonicalResponse)
            canonicalUri = canonicalResponseObj["canonicalURI"]
            canonicalLanguageURI = canonicalResponseObj["canonicalLanguageURI"]
            language = canonicalResponseObj["language"]

            localParams = {'canonicalLanguageURI': canonicalLanguageURI, 'localURI': 'http://localhost:8181/wiki/Item:Q1', 'storageName': 'wikibase'}
            localResponse = requests.post("http://localhost:9326/uri-factory/local",params=localParams).content
            localResponseObj = json.loads(localResponse)
            print(localResponseObj)
            """