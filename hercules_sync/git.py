from urllib.parse import urlencode

import base64
import json
import urllib3

from unidiff import PatchSet


GITHUB_BASE_URL = 'https://github.com'
GITHUB_API_URL = 'https://api.github.com'

USER_AGENT = 'weso'

class GitPushEventHandler():
    """ Processes information from a GitHub push event.

    Parameters
    ----------
    data : dict
        Data obtained from a GitHub WebHook regarding a push event.
    """

    def __init__(self, data, oauth=''):
        self.before_commit = data['before']
        self.after_commit = data['after']
        self.repo_name = data['repository']['full_name']
        self.diff_parser = GitDiffParser(self.repo_name,
                                         self.before_commit,
                                         self.after_commit)
        self.diff_parser.load_diff()
        self.data_loader = GitDataLoader(self.repo_name,
                                         self.before_commit,
                                         self.after_commit,
                                         oauth)

    @property
    def added_files(self):
        """ Files added in the push.

        Returns
        -------
        Generator of :obj: `GitFile`
            Generator with GitFile objects which contain information
            about each added file.
        """
        added_files = self.diff_parser.patch.added_files
        return self._git_loader_iterator(added_files)

    @property
    def modified_files(self):
        """ Files modified in the push.

        Returns
        -------
        iterable of :obj: `GitFile`
            Iterable with GitFile objects which contain information
            about each modified file.
        """
        modified_files = self.diff_parser.patch.modified_files
        return self._git_loader_iterator(modified_files)

    @property
    def removed_files(self):
        """ Files modified in the push.

        Returns
        -------
        iterable of :obj: `GitFile`
            Iterable with GitFile objects which contain information
            about each modified file.
        """
        removed_files = self.diff_parser.patch.removed_files
        return self._git_loader_iterator(removed_files)

    def _git_loader_iterator(self, patched_files):
        for gitfile in self.data_loader.load_files(patched_files):
            yield gitfile

class GitFile():
    """ Encapsulates the content of a file and the git diff information.

    Parameters
    ----------
    patched_file : :obj:`unidiff.PatchFile`
        PatchFile instance.
    source_content : str
        Original content of the file before the push (source).
    target_content : str
        Final content of the file after the push (target).
    """

    def __init__(self, patched_file, source_content, target_content):
        self._patched_file = patched_file
        self.source_content = source_content
        self.target_content = target_content

    @property
    def path(self):
        return self._patched_file.path

    @property
    def added_lines(self):
        """ Return the list of added lines from the file

        Returns
        -------
        list of (str, int)
            List of tuples where each tuple contains the content of the added
            line and the number of the line in the target file.
        """
        return [(line.value, line.target_line_no)
                for hunk in self._patched_file
                for line in hunk if line.is_added]

    @property
    def removed_lines(self):
        """ Return the list of removed lines from the file

        Returns
        -------
        list of (str, int)
            List of tuples where each tuple contains the content of the removed
            line and the number of the line in the source file.
        """
        return [(line.value, line.source_line_no)
                for hunk in self._patched_file
                for line in hunk if line.is_removed]

    def _get_lines(self, line_filter):
        return [(line.value, line.target_line_no)
                for hunk in self._patched_file
                for line in hunk if line_filter(line)]

    def __str__(self):
        rval = [self.path]
        rval.append('\nAdded lines: ')
        rval.append(str(self.added_lines))
        rval.append('Removed lines: ')
        rval.append(str(self.removed_lines))
        rval.append('\nOriginal content: ')
        rval.append(self.source_content)
        rval.append('\nFinal content: ')
        rval.append(self.target_content)
        return '\n'.join(rval)


class GitDiffParser():
    """ Return Diff information from a repository.

    Parameters
    ----------
    repo_full_name : str
        Full name of the github repository (must follow the
        form 'user_name/repo_name').
    before_commit : str
        Sha of the initial commit before the push.
    after_ref : str
        Sha of the final commit after the push.
    """

    def __init__(self, repo_full_name, before_commit, after_commit):
        self.compare_url = self._build_compare_url(repo_full_name,
                                                   before_commit,
                                                   after_commit)
        self.patch = None

    def load_diff(self):
        """

        Returns
        -------
        :obj: `unidiff.PatchSet`
            PatchSet instance with the diff information.
        """
        req = self._send_request()
        if req.status == 404:
            raise DiffNotFoundError()

        diff = req.data.decode("utf-8")
        self.patch = PatchSet(diff)

    def _build_compare_url(self, repo_name, before_commit, after_commit):
        return '{0}/{1}/compare/{2}...{3}.diff'.format(GITHUB_BASE_URL, repo_name,
                                                       before_commit, after_commit)

    def _send_request(self):
        http = urllib3.PoolManager()
        return http.request(
            'GET',
            self.compare_url,
            headers={
                'User-Agent': USER_AGENT
            }
        )

class GitDataLoader():
    """ Downloads github files from a commit, before and after a push.

    This class is used to download files from a github repository given a certain
    original (before_ref) and final commit (after_ref).

    Parameters
    ----------
    repo_name : str
        Full name of the github repository where the files are located.
    before_ref : str
        Sha of the initial commit before the push.
    after_ref : str
        Sha of the final commit after the push.
    """

    NO_COMMIT_MSG = "No commit found for the ref"
    NOT_FOUND_MSG = "Not Found"

    def __init__(self, repo_name, before_ref, after_ref, oauth=''):
        self.repo_name = repo_name
        self.before_ref = before_ref
        self.after_ref = after_ref
        self.oauth = oauth
        self.http = urllib3.PoolManager()

    def load_files(self, files_to_load):
        """ Downloads the given files, returning them inside GitFile objects.

        Parameters
        ----------
        files_to_load : list of :obj:`unidiff.PatchFile`
            Iterable containing instances of patchfile objects.

        Yields
        -------
        :obj:`GitFile`
            Generator that returns one instance of the GitFile class for each
            downloaded file from GitHub.
        """
        return (GitFile(patched_file,
                        self._load_file(patched_file.path, self.before_ref),
                        self._load_file(patched_file.path, self.after_ref))
                for patched_file in files_to_load)

    def _load_file(self, file_path, ref):
        download_url = self._build_download_url(file_path, ref)

        req = self._send_request(download_url)
        json_response = json.loads(req.data.decode('utf-8'))

        if 'message' in json_response:
            message = json_response['message']
            if GitDataLoader.NOT_FOUND_MSG in message:
                return ''
            if GitDataLoader.NO_COMMIT_MSG in message:
                err_msg = f"Commit {ref} was not found for repository '{self.repo_name}'."
                raise InvalidCommitError(err_msg)

        content = json_response['content']
        decoded_content = base64.b64decode(content).decode('utf-8')
        return decoded_content

    def _build_download_url(self, file_path, ref):
        args = urlencode({'ref': ref})
        return '{0}/repos/{1}/contents/{2}?{3}'.format(
            GITHUB_API_URL, self.repo_name, file_path, args)

    def _send_request(self, url):
        return self.http.request(
            'GET',
            url,
            headers={
                'User-Agent': USER_AGENT,
                'Authorization': f'token {self.oauth}'
            }
        )

class DiffNotFoundError(Exception):
    """ Exception subclass used when a diff file cannot be found from the server """

class InvalidCommitError(Exception):
    """ Exception subclass that represents the use of an invalid commit when loading a file """
