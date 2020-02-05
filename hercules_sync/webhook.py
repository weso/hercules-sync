""" Webhook module
"""

import collections
import hashlib
import hmac
import six

from flask import abort, request

EVENT_HEADER = "X-Github-Event"
SIGN_HEADER = "X-Hub-Signature"

class WebHook():
    """ Class to manage Github webhooks from a Flask app.
    """

    def __init__(self, app, endpoint, key):
        app.add_url_rule(rule=endpoint, endpoint=endpoint,
                         view_func=self._on_request,
                         methods=['POST'])
        print(key)
        self._hooks = collections.defaultdict(list)
        self.key = key

    def hook(self, event="push"):
        """ Add a function to process a webhook event.

        Params
        ------
        event: str. Type of event to be listened to.
        """
        def decorator(fun):
            self._hooks[event].append(fun)
            return fun
        return decorator

    def _is_signature_valid(self, signature, data):
        secret_gen = _create_secret_gen_from(self.key, data)
        digest = "sha1=" + secret_gen.hexdigest()
        return digest == signature

    def _on_request(self):
        data = request.data
        if data is None:
            abort(400)

        signature = _try_get_header(request, SIGN_HEADER, "")
        if not self._is_signature_valid(signature, request.data):
            abort(400, "Invalid signature")

        event = _try_get_header(request, EVENT_HEADER,
                                "There was no event received.")

        for fun in self._hooks[event]:
            fun(data)
        return "", 204


def _create_secret_gen_from(key, data):
    if not isinstance(key, six.binary_type):
        key = key.encode("utf-8")

    return hmac.new(key, data, digestmod=hashlib.sha1)

def _try_get_header(req, header, err_msg):
    try:
        return req.headers[header]
    except KeyError:
        abort(400, err_msg)
