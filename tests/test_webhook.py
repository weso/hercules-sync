from unittest import mock

import pytest
import werkzeug

from hercules_sync.webhook import WebHook

@pytest.fixture
def mocked_req():
    with mock.patch("hercules_sync.webhook.request") as req:
        req.headers = {
            'content-type': 'application/json',
            'X-Hub-Signature': 'sha1=61620b06f590da1915eb1f802f9ea701aea5a4d4',
            'X-Github-Event': 'push'
        }
        req.data = b'{"ref": "head", "before": "001", "after": "002"}'
        yield req

@pytest.fixture
def app():
    return mock.Mock()

@pytest.fixture
def webhook(app):
    return WebHook(app, endpoint='/postreceive', key='abc')

def test_url_rule_is_added(app):
    route = '/test'
    webhook = WebHook(app, endpoint=route, key='')
    app.add_url_rule.assert_called_once_with(rule=route, endpoint=route,
                                             view_func=webhook._on_request,
                                             methods=['POST'])

def test_invalid_content_type(mocked_req, webhook):
    mocked_req.headers['content-type'] = "application/x-www-form-urlencoded"

    _assert_request_fails(webhook, "Invalid content format")

def test_invalid_json(mocked_req, webhook):
    mocked_req.data = b'this is not a valid {} [] json'
    mocked_req.headers['X-Hub-Signature'] = 'sha1=fc8dfa90e04c816a8fb98331fe14bc629a602985'
    _assert_request_fails(webhook, "error parsing the json")

def test_invalid_signature(mocked_req, webhook):
    mocked_req.headers['X-Hub-Signature'] = "invented"
    _assert_request_fails(webhook, "Invalid signature")

def test_no_headers(mocked_req, webhook):
    del mocked_req.headers['X-Github-Event']
    _assert_request_fails(webhook, "no event")

    del mocked_req.headers['content-type']
    _assert_request_fails(webhook, "no content")

    del mocked_req.headers['X-Hub-Signature']
    _assert_request_fails(webhook, "no signature")

def test_handler_not_called_with_different_event(mocked_req, webhook):
    mocked_req.headers['X-Github-Event'] = "pull_request"
    handler = mock.Mock()
    webhook.hook()(handler)
    webhook._on_request()
    handler.assert_not_called()


def test_handler_called_with_valid_event(mocked_req, webhook):
    handler = mock.Mock()
    webhook.hook()(handler)
    webhook._on_request()
    handler.assert_called_once()

def test_multiple_handlers(mocked_req, webhook):
    handlers = []
    for _ in range(10):
        handler = mock.Mock()
        webhook.hook()(handler)
        handlers.append(handler)
    webhook._on_request()
    for handler in handlers:
        handler.assert_called_once()

def _assert_request_fails(hook, err_msg):
    with pytest.raises(werkzeug.exceptions.BadRequest) as excpt:
        hook._on_request()
    assert err_msg in str(excpt.value)
