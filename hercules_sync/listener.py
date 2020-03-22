from flask import current_app as app
from flask import abort

from .git import GitPushEventHandler
from .webhook import WebHook

WEBHOOK = WebHook(app, endpoint='/postreceive', key=app.config['SECRET_KEY'])

@WEBHOOK.hook()
def on_push(data):
    print("Got push with: {0}".format(data))

    try:
        git_handler = GitEventHandler(data)
    except:
        abort(404)
    return 200, 'Ok'
