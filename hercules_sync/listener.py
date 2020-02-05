from flask import current_app as app
from .webhook import WebHook

WEBHOOK = WebHook(app, endpoint='/postreceive', key=app.config['SECRET_KEY'])

@WEBHOOK.hook()
def on_push(data):
    print("Got push with: {0}".format(data))
