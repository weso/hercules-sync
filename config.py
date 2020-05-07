""" Configuration module for the flask app.

Each class represents a configuration to use by the flask app
created in hercules_sync/__init__.py.
"""

from hercules_sync.secret import USERNAME, PASSWORD, SECRET_KEY, WESOBOT_TOKEN

class BaseConfig():
    DEBUG = False
    TESTING = False
    WBUSER = USERNAME
    WBPASS = PASSWORD
    WEBHOOK_SECRET = SECRET_KEY
    WESOBOT_OAUTH = WESOBOT_TOKEN

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'
    WBAPI = 'http://156.35.94.149:8181/w/api.php'
    WBSPARQL = 'http://156.35.94.149:8282/proxy/wdqs/bigdata/namespace/wdq/sparql'

class ProductionConfig(BaseConfig):
    ENV = 'production'
    WBAPI = ''
    WBSPARQL = ''

class TestingConfig(BaseConfig):
    TESTING = True
    ENV = 'testing'
