from unittest import mock

import base64
import json
import os
import pytest

from hercules_sync.git import GitDataLoader, GitDiffParser, \
                              GitPushEventHandler, \
                              DiffNotFoundError, InvalidCommitError

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SOURCE_DIR = 'source'
TARGET_DIR = 'target'

def fake_load_file(file_path):
    """ Mock function to load the test files and return them in a json response """
    file = os.path.join(DATA_DIR, file_path)
    with open(file, 'rb') as fp:
        file_content = fp.read()
        encoded_file_content = base64.b64encode(file_content).decode()

        response = mock.Mock()
        response.data = json.dumps({"content": encoded_file_content}).encode('utf-8')
        return response

@pytest.fixture
def mocked_diff_parser():
    file_path = os.path.join(DATA_DIR, 'test_diff.diff')
    diff_parser = GitDiffParser('', SOURCE_DIR, TARGET_DIR)

    fake_response = mock.Mock()
    fake_response.data = open(file_path, 'r').read().encode('utf-8')

    diff_parser._send_request = mock.MagicMock(return_value=fake_response)
    return diff_parser

@pytest.fixture
def mocked_data_loader():
    data_loader = GitDataLoader('', SOURCE_DIR, TARGET_DIR)
    data_loader._build_download_url = lambda file_path, ref: os.path.join(ref, file_path)
    data_loader._send_request = lambda url: fake_load_file(url)
    return data_loader

@pytest.fixture
def mocked_event_handler(mocked_diff_parser, mocked_data_loader):
    with mock.patch.object(GitPushEventHandler, "__init__", lambda _, data: None):
        event_handler = GitPushEventHandler('')
        event_handler.diff_parser = mocked_diff_parser
        event_handler.diff_parser.load_diff()
        event_handler.data_loader = mocked_data_loader
        return event_handler

def test_added_files(mocked_event_handler):
    added_files = list(mocked_event_handler.added_files)
    assert len(added_files) == 1
    assert added_files[0].path == 'ShExL.interp'
    assert added_files[0].source_content == ''

def test_added_lines(mocked_event_handler):
    test_file = list(mocked_event_handler.added_files)[0]
    added_lines = test_file.added_lines
    assert len(added_lines) == 17

    assert ('token literal names:\n', 1) in added_lines
    assert ('null\n', 2) in added_lines
    assert ('null\n', 17) in added_lines

def test_data_loader_build_url():
    data_loader = GitDataLoader('user_name/repo_name', '1234', '5678')
    expected = 'https://api.github.com/repos/user_name/repo_name/contents/myfile.txt?ref=1234'
    assert data_loader._build_download_url('myfile.txt', '1234') == expected

def test_data_loader_invalid_commit(mocked_event_handler):
    bef_ref = '1234'
    after_ref = '5678'
    data_loader = GitDataLoader('', bef_ref, after_ref)
    response = mock.Mock()
    response.data = json.dumps({
        "message": 'No commit found for the ref {}'.format(bef_ref)
    }).encode('utf-8')
    data_loader._send_request = lambda url: response
    mocked_event_handler.data_loader = data_loader
    with pytest.raises(InvalidCommitError) as err:
        _ = list(mocked_event_handler.added_files)
    assert f"Commit {bef_ref} was not found" in str(err.value)

def test_data_loader_invalid_file():
    loader = GitDataLoader('', '', '')
    response = mock.Mock()
    response.data = json.dumps({
        "message": 'Not Found'
    }).encode('utf-8')
    loader._send_request = lambda url: response
    assert loader._load_file('invented_file.txt', '4567') == ''

def test_diff_parser_build_url():
    diff_parser = GitDiffParser('user_name/repo_name', '1234', '5678')
    assert diff_parser.compare_url == 'https://github.com/user_name' \
                                      '/repo_name/compare/1234...5678.diff'

def test_diff_parser_diff_not_found(mocked_diff_parser):
    response = mock.Mock()
    response.status = 404
    mocked_diff_parser._send_request = lambda: response
    with pytest.raises(DiffNotFoundError):
        mocked_diff_parser.load_diff()

def test_event_handler_init():
    data = {
        'before': '1234',
        'after': '5678',
        'repository': {
            'full_name': 'user_name/repo_name'
        }
    }
    with pytest.raises(DiffNotFoundError):
        handler = GitPushEventHandler(data)
        assert handler.before_commit == '1234'
        assert handler.after_commit == '5678'
        assert handler.repo_name == 'user_name/repo_name'

def test_gitfile_str(mocked_event_handler):
    test_file = list(mocked_event_handler.added_files)[0]
    str_representation = str(test_file)
    assert "Added lines" in str_representation
    assert str(test_file.path) in str_representation
    assert "(\"'PREFIX'\\n\", 3)" in str_representation

def test_modified_files(mocked_event_handler):
    modif_files = list(mocked_event_handler.modified_files)
    assert len(modif_files) == 1
    assert modif_files[0].path == 'ASTBasicTest.txt'

def test_removed_lines(mocked_event_handler):
    test_file = list(mocked_event_handler.removed_files)[0]
    removed_lines = test_file.removed_lines
    assert len(removed_lines) == 6
    assert ('package es.weso.shexl\n', 1) in removed_lines
    assert ('\n', 2) in removed_lines
    assert ('\n', 4) in removed_lines

def test_removed_files(mocked_event_handler):
    removed_files = list(mocked_event_handler.removed_files)
    assert len(removed_files) == 1
    assert removed_files[0].path == 'definitions.txt'
    assert removed_files[0].target_content == ''
