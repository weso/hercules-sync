import logging

from typing import List

from flask import current_app as app
from flask import abort
from flask_executor import Executor

from .git import GitFile, GitPushEventHandler, DiffNotFoundError
from wbsync.synchronization import GraphDiffSyncAlgorithm, OntologySynchronizer
from wbsync.triplestore import WikibaseAdapter
from .webhook import WebHook
from .uris_factory import HerculesURIsFactory

EXECUTOR = Executor(app)
LOGGER = logging.getLogger(__name__)
WEBHOOK = WebHook(app, endpoint='/postreceive', key=app.config['WEBHOOK_SECRET'])

@WEBHOOK.hook()
def on_push(data):
    try:
        LOGGER.info("Got push with: %s", data)
        git_handler = GitPushEventHandler(data, app.config['GITHUB_OAUTH'])
        ontology_files = _extract_ontology_files(git_handler, 'ttl', None)
        LOGGER.info("Modified files: %s", ontology_files)
    except DiffNotFoundError:
        LOGGER.info("There was no diff to synchronize.")
        return 200, 'No diff'
    except Exception as excpt:
        LOGGER.exception("There was an error processing the request.")
        abort(404)

    if len(ontology_files) > 0:
        EXECUTOR.submit(_synchronize_files, ontology_files)
    return 200, 'Ok'

def _extract_ontology_files(git_handler: GitPushEventHandler, file_format: str,
                            custom_filter=None) -> List[GitFile]:
    LOGGER.info("Extracting ontology files modified from push...")
    all_files = list(git_handler.removed_files) + list(git_handler.added_files) + \
        list(git_handler.modified_files)
    if custom_filter:
        return custom_filter(all_files)
    return list(filter(lambda x: x._patched_file.path.endswith(f".{file_format}"), all_files))

def _synchronize_files(files: List[GitFile]):
    LOGGER.info("Synchronizing files...")
    algorithm = GraphDiffSyncAlgorithm()
    adapter = WikibaseAdapter(app.config['WBAPI'], app.config['WBSPARQL'],
                              app.config['WBUSER'], app.config['WBPASS'],factory_of_uris=HerculesURIsFactory())
    for file in files:
        synchronizer = OntologySynchronizer(algorithm)
        ops = synchronizer.synchronize(file.source_content, file.target_content)
        for op in ops:
            res = op.execute(adapter)
            if not res.successful:
                LOGGER.warning("Error synchronizing triple: %s", res.message)
    LOGGER.info("Synchronization finished.")

def _filter_asio_files(all_files: List[GitFile]) -> List[GitFile]:
    return list(filter(lambda x: "current/asio.ttl" in x._patched_file.path, all_files))
