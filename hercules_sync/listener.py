from flask import current_app as app
from flask import abort

from .git import GitPushEventHandler
from .webhook import WebHook

WEBHOOK = WebHook(app, endpoint='/postreceive', key=app.config['SECRET_KEY'])

@WEBHOOK.hook()
def on_push(data):
    try:
        git_handler = GitPushEventHandler(data)
    except:
        abort(404)
    return 200, 'Ok'
