""" hercules_sync package __init__ file
"""

import os

from flask import Flask


CONFIG = {
    "base": "config.BaseConfig",
    "development": "config.DevelopmentConfig",
    "production": "config.ProductionConfig",
    "testing": "config.TestingConfig"
}

def create_app():
    """ Factory to create the flask application and load the config.

    By default config.BaseConfig is used. In order to change this config
    the FLASK_CONFIG environment variable must be changed to match one of
    the keys in the CONFIG dict.

    Returns
    -------
    app: Flask.app object
    """
    app = Flask(__name__, instance_relative_config=True)
    config_name = os.getenv('FLASK_CONFIG', 'base')
    app.config.from_object(CONFIG[config_name])
    with app.app_context():
        from .listener import WEBHOOK
    return app
