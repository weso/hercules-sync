""" Webhook module
"""

import collections
import hashlib
import hmac
import json
import six

from flask import abort, request

CONTENT_HEADER = "content-type"
EVENT_HEADER = "X-Github-Event"
SIGN_HEADER = "X-Hub-Signature"

class WebHook():
    """ Class to manage Github webhooks from a Flask app.
    """

    def __init__(self, app, endpoint, key):
        app.add_url_rule(rule=endpoint, endpoint=endpoint,
                         view_func=self._on_request,
                         methods=['POST'])
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
        signature = _try_get_header(request, SIGN_HEADER,
                                    "There is no signature header.")
        if not self._is_signature_valid(signature, request.data):
            abort(400, "Invalid signature")


        content_type = _try_get_header(request, CONTENT_HEADER,
                                       "There is no content header.")
        if content_type != "application/json":
            abort(400, "Invalid content format. Only application/json " \
                  "is supported")

        data = _load_request_data(request)
        if data is None:
            abort(400)

        event = _try_get_header(request, EVENT_HEADER,
                                "There was no event received.")

        for fun in self._hooks[event]:
            fun(data)
        return "", 204


def _create_secret_gen_from(key, data):
    if not isinstance(key, six.binary_type):
        key = key.encode("utf-8")

    return hmac.new(key, data, digestmod=hashlib.sha1)

def _load_request_data(req):
    data = req.data
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        abort(400, "There was an error parsing the json data.")

def _try_get_header(req, header, err_msg):
    try:
        return req.headers[header]
    except KeyError:
        abort(400, err_msg)
