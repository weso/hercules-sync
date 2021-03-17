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
        id = requests.post("http://localhost:9326/canonical-uri?concept=labra&domain=hercules.org&subDomain=um&typeCode=res").content
        propId = requests.post(
            "http://localhost:9326/canonical-uri?property=instanceOf&domain=hercules.org&subDomain=um&typeCode=res").content
        print(id)

    propId = requests.post(
        "http://localhost:9326/canonical-uri?concept=Paco&domain=hercules.org&subDomain=um&typeCode=res").content

    print(propId)
    responseObj = json.loads(propId)
    if (len(responseObj) > 0):
        print(responseObj["id"])
    response= requests.get("http://localhost:9326/canonical-uri?concept=labra").content
    response1 = requests.get("http://localhost:9326/canonical-uri?property=labra").content

    import re
    name = 'propiedadNueva'
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower().replace("_","-")

    response3 = requests.get("http://localhost:9326/canonical-uri?reference="+name).content

    print(response3)


        responseObj = json.loads(response)
        if(len(responseObj)>0):
            print(responseObj[0]["id"])
    """

