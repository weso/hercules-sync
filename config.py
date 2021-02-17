""" Configuration module for the flask app.

Each class represents a configuration to use by the flask app
created in hercules_sync/__init__.py.
"""

import os

from wbsync.util.error import InvalidConfigError

def _try_get_config_from_env(config_key):
    if config_key not in os.environ:
        raise InvalidConfigError(f"{config_key} environment variable is not set.")
    return os.environ[config_key]

class BaseConfig():
    DEBUG = False
    TESTING = False
    GITHUB_OAUTH = _try_get_config_from_env('GITHUB_OAUTH')
    WBAPI = _try_get_config_from_env('WBAPI')
    WBSPARQL = _try_get_config_from_env('WBSPARQL')
    WBUSER = _try_get_config_from_env('WBUSER')
    WBPASS = _try_get_config_from_env('WBPASS')
    WEBHOOK_SECRET = _try_get_config_from_env('WEBHOOK_SECRET')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'

class ProductionConfig(BaseConfig):
    ENV = 'production'

class TestingConfig(BaseConfig):
    TESTING = True
    ENV = 'testing'
