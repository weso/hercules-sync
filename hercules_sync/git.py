from urllib.parse import urljoin
from unidiff import PatchSet

import tempfile
import urllib3


GITHUB_BASE_URL = 'https://api.github.com'

class GitEventHandler():
    def __init__(self, data):
        self.before_commit = data['before']
        self.after_commit = data['after']
        self.repo_name = data['repository']['full_name']
        self.diff_parser = GitDiffParser(self.repo_name,
                                         self.before_commit,
                                         self.after_commit)

    def added_files(self):
        added_files = self.diff_parser.patch.added_files
        yield self._git_loader_iterator(added_files)

    def modified_files(self):
        modified_files = self.diff_parser.patch.modified_files
        yield self._git_loader_iterator(modified_files)

    def removed_files(self):
        removed_files = self.diff_parser.patch.removed_files
        yield self._git_loader_iterator(removed_files)

    def _git_loader_iterator(self, files):
        with GitDataLoader(self.repo_name, files) as loaded_files:
            for file in loaded_files:
                yield file.read()

class GitDiffParser():
    def __init__(self, repo_name, before_commit, after_commit):
        self.compare_url = self._build_compare_url(repo_name, before_commit,
                                                   after_commit)
        self.load_diff()
        self._assert_valid_data()

    def load_diff(self):
        http = urllib3.PoolManager()
        req = http.request(
            'GET',
            self.compare_url,
            headers={
                'Accept': 'application/vnd.github.v3.diff'
            }
        )
        # parse response status
        diff = req

        self.patch = PatchSet(diff)

    def _build_compare_url(self, repo_name, before_commit, after_commit):
        return '{0}/{1}/{2}/{3}..{4}'.format(GITHUB_BASE_URL, repo_name, 'compare',
                                             before_commit, after_commit)

    def _assert_valid_data(self):
        pass

class GitDataLoader():
    def __init__(self, repo_name, files_to_load):
        self.repo_name = repo_name
        self.files_to_load = files_to_load
        self.file_pointers = []
        self.dir_p = tempfile.TemporaryDirectory()

    def __enter__(self):
        http = urllib3.PoolManager()
        return [self._load_file(file_name, http) for file_name
                in self.files_to_load]

    def __exit__(self, type, data, value):
        for pointer in self.file_pointers:
            pointer.close()
        self.dir_p.cleanup()

    def _load_file(self, file_name, http):
        download_url = '{0}/{1}/{2}/{3}'.format(GITHUB_BASE_URL, self.repo_name,
                                                "contents", file_name)
        req = http.request('GET', download_url)
        fp = tempfile.TemporaryFile(dir=self.dir_p)
        fp.write(req['data'])
        self.file_pointers.append(fp)
        return fp
