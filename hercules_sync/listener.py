from flask import current_app as app
from flask import abort

from .git import GitPushEventHandler
from .webhook import WebHook

WEBHOOK = WebHook(app, endpoint='/postreceive', key=app.config['SECRET_KEY'])

@WEBHOOK.hook()
def on_push(data):
    #print("Got push with: {0}".format(data))

    try:
        git_handler = GitPushEventHandler(data)
        show_results(git_handler)
        update_ontology(git_handler)
    except:
        abort(404)
    return 200, 'Ok'

def update_ontology(git_handler):
    #ontology_sync = OntologySynchronizer()
    #
    # this needs to be refactored, for now its just here
    # to make a high level idea of how it should work
    #for file in git_handler.modified_files:
    #    ontology_sync.update_ontology(file)
    #for file in git_handler.removed_files:
    #    ontology_sync.remove_ontology(file)
    #for file in git_handler.added_files:
    #    ontology_sync.add_ontology(file)
    pass

def show_results(git_handler: GitPushEventHandler):
    print_files("Modified_files", git_handler.modified_files)
    print_files("Removed files", git_handler.removed_files)
    print_files("Added files", git_handler.added_files)

def print_files(title, files):
    separator = "-" * 50
    print(separator, title, separator, sep='\n')
    for file in files:
        if file.path.endswith('owl'):
            print(file)
