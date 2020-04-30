import logging

from typing import List

from flask import current_app as app
from flask import abort

from .git import GitFile, GitPushEventHandler
from .synchronization import GraphDiffSyncAlgorithm, OntologySynchronizer
from .triplestore import WikibaseAdapter
from .webhook import WebHook

LOGGER = logging.getLogger(__name__)
WEBHOOK = WebHook(app, endpoint='/postreceive', key=app.config['SECRET_KEY'])

@WEBHOOK.hook()
def on_push(data):
    try:
        LOGGER.info("Got push with: %s", data)
        git_handler = GitPushEventHandler(data)
        ontology_files = _extract_ontology_files(git_handler, file_format='ttl')
        _synchronize_files(ontology_files)
    except:
        abort(404)
    return 200, 'Ok'

def _extract_ontology_files(git_handler: GitPushEventHandler, file_format: str) -> List[GitFile]:
    all_files = list(git_handler.removed_files) + list(git_handler.added_files) + \
        list(git_handler.modified_files)
    return list(filter(lambda x: x._patched_file.path.endswith(f".{file_format}"), all_files))

def _synchronize_files(files: List[GitFile]):
    algorithm = GraphDiffSyncAlgorithm()
    adapter = WikibaseAdapter(app.config['WBAPI'], app.config['WBSPARQL'],
                              app.config['WBUSER'], app.config['WBPASS'])
    for file in files:
        synchronizer = OntologySynchronizer(algorithm)
        ops = synchronizer.synchronize(file)
        for op in ops:
            res = op.execute(adapter)
            if not res.successful:
                LOGGER.warning("Error synchronizing triple: %s", res.message)
