from unittest import mock

from hercules_sync.git import GitDataLoader, GitDiffParser, \
                              GitFile, GitPushEventHandler

import base64
import json
import os
import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SOURCE_DIR = 'source'
TARGET_DIR = 'target'

def fake_load_file(file_path):
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
    data_loader._send_request = lambda http, url: fake_load_file(url)
    return data_loader

@pytest.fixture
def mocked_event_handler(mocked_diff_parser, mocked_data_loader):
    with mock.patch.object(GitPushEventHandler, "__init__", lambda _, data: None):
        event_handler = GitPushEventHandler('')
        event_handler.diff_parser = mocked_diff_parser
        event_handler.diff_parser.load_diff()
        event_handler.data_loader = mocked_data_loader
        return event_handler

def test_added_lines(mocked_event_handler):
    test_file = list(mocked_event_handler.added_files)[0]
    added_lines = test_file.added_lines
    assert len(added_lines) == 17

    assert ('token literal names:\n', 1) in added_lines
    assert ('null\n', 2) in added_lines
    assert ('null\n', 17) in added_lines

def test_removed_lines(mocked_event_handler):
    test_file = list(mocked_event_handler.removed_files)[0]
    removed_lines = test_file.removed_lines
    print(removed_lines)
    assert len(removed_lines) == 6
    assert ('package es.weso.shexl\n', 1) in removed_lines
    assert ('\n', 2) in removed_lines
    assert ('\n', 4) in removed_lines

def test_diff_loader_build_url():
    diff_parser = GitDiffParser('user_name/repo_name', '1234', '5678')
    assert diff_parser.compare_url == 'https://github.com/user_name' \
                                      '/repo_name/compare/1234...5678.diff'

def test_added_files(mocked_event_handler):
    added_files = list(mocked_event_handler.added_files)
    assert len(added_files) == 1
    assert added_files[0].path == 'ShExL.interp'
    assert added_files[0].source_content == ''

def test_modified_files(mocked_event_handler):
    modif_files = list(mocked_event_handler.modified_files)
    assert len(modif_files) == 1
    assert modif_files[0].path == 'ASTBasicTest.txt'

def test_removed_files(mocked_event_handler):
    removed_files = list(mocked_event_handler.removed_files)
    assert len(removed_files) == 1
    assert removed_files[0].path == 'definitions.txt'
    print(removed_files[0])
    assert removed_files[0].target_content == ''

def test_data_loader_invalid_file():
    #loader = GitDataLoader()
    pass

def test_data_loader_build_url():
    pass

def test_data_loader_invalid_commit():
    pass

def test_git_parser_invalid_request():
    pass

def test_git_parser_valid_request():
    pass

def test_gitfile_str():
    pass
