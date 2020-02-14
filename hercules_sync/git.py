from urllib.parse import urlencode

import base64
import json
import tempfile
import urllib3

from unidiff import PatchSet


GITHUB_BASE_URL = 'https://github.com'
GITHUB_API_URL = 'https://api.github.com'

USER_AGENT = 'weso'

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
        return self._git_loader_iterator(added_files, self.after_commit)

    def modified_files(self):
        modified_files = self.diff_parser.patch.modified_files
        return self._git_loader_iterator(modified_files, self.after_commit)

    def removed_files(self):
        removed_files = self.diff_parser.patch.removed_files
        return self._git_loader_iterator(removed_files, self.before_commit)

    def _git_loader_iterator(self, patched_files, ref):
        with GitDataLoader(self.repo_name, patched_files, ref) as loaded_files:
            print('Loaded files: ', loaded_files)
            for i, file in enumerate(loaded_files):
                yield GitFile(patched_files[i], file.read())

class GitFile():
    """ Encapsulates the content of a file and the git diff information.
    """

    def __init__(self, patched_file, file_content):
        self.patched_file = patched_file
        self.content = file_content

    def added_lines(self):
        return [(line.value, line.target_line_no)
                for hunk in self.patched_file
                for line in hunk if line.is_added]

    def removed_lines(self):
        return [(line.value, line.source_line_no)
                for hunk in self.patched_file
                for line in hunk if line.is_removed]

    def _get_lines(self, line_filter):
        return [(line.value, line.target_line_no)
                for hunk in self.patched_file
                for line in hunk if line_filter(line)]


class GitDiffParser():
    def __init__(self, repo_name, before_commit, after_commit):
        self.compare_url = self._build_compare_url(repo_name, before_commit,
                                                   after_commit)
        self.load_diff()
        self._assert_valid_data()

    def load_diff(self):
        http = urllib3.PoolManager()
        print(self.compare_url)
        req = http.request(
            'GET',
            self.compare_url,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        # parse response status
        diff = req.data.decode("utf-8")
        print('Diff: ', diff)

        self.patch = PatchSet(diff)

    def _build_compare_url(self, repo_name, before_commit, after_commit):
        return '{0}/{1}/{2}/{3}...{4}.diff'.format(GITHUB_BASE_URL, repo_name, 'compare',
                                                   before_commit, after_commit)

    def _assert_valid_data(self):
        # TODO
        pass

class GitDataLoader():
    def __init__(self, repo_name, files_to_load, ref=None):
        self.repo_name = repo_name
        self.files_to_load = files_to_load
        self.ref = ref
        self.file_pointers = []
        self.dir_p = tempfile.TemporaryDirectory()

    def __enter__(self):
        http = urllib3.PoolManager()
        return [self._load_file(file_name, http) for file_name
                in self.files_to_load]

    def __exit__(self, typ, data, value):
        for pointer in self.file_pointers:
            pointer.close()
        self.dir_p.cleanup()

    def _load_file(self, file_name, http):
        args = urlencode({'ref': self.ref})
        download_url = '{0}/repos/{1}/contents/{2}?{3}'.format(
            GITHUB_API_URL, self.repo_name, file_name.path, args)
        req = http.request(
            'GET',
            download_url,
            headers={
                'User-Agent': USER_AGENT
            }
        )
        fp = tempfile.TemporaryFile(dir=self.dir_p.name)
        content = json.loads(req.data.decode('utf-8'))['content']
        decoded_content = base64.b64decode(content)
        fp.write(decoded_content)
        self.file_pointers.append(fp)
        return fp
