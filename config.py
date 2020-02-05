""" Configuration module for the flask app.

Each class represents a configuration to use by the flask app
created in hercules_sync/__init__.py.
"""

class BaseConfig():
    DEBUG = False
    TESTING = False

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    ENV = 'development'

class ProductionConfig(BaseConfig):
    ENV = 'production'

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    ENV = 'testing'
