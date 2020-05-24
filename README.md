# hercules-sync
<table>
<tr>
  <td>License</td>
  <td>
    <a href="https://github.com/weso/hercules-sync/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/weso/hercules-sync.svg" alt="license" />
    </a>
</td>
</tr>
<tr>
  <td>Build Status</td>
  <td>
    <a href="https://travis-ci.org/weso/hercules-sync">
    <img src="https://travis-ci.org/weso/hercules-sync.svg?branch=master" alt="travis build status" />
    </a>
  </td>
</tr>
<tr>
  <td>Coverage</td>
  <td>
    <a href="https://codecov.io/gh/weso/hercules-sync">
    <img src="https://codecov.io/gh/weso/hercules-sync/branch/master/graph/badge.svg" alt="coverage" />
    </a>
  </td>
</tr>
</table>

Tools to synchronise data between the ontology files and Wikibase instance for the Hercules project at University of Murcia.

## Directory structure
* docs: Development documentation of this module.
* hercules_sync: Source code of the application.
* tests: Test suite used to validate the project.

## Defining a webhook in the source repo
In order to perform the synchronization automatically, a webhook must be created in the original repository where the ontology is stored. This webhook will be launched whenever a new push event occurs in the repo, and the synchronization service will be called to sync the changes with the wikibase instance. When creating a new webhook, the payload url must point to the URL where this server will be available. It is also important to define a secret key that will be used to accept only requests from the source repo and not from other ones. An example configuration will look like this one:
![](docs/images/webhook_example.png)

## Launching the app with Docker
In order to execute the app you need to set the following configuration in the docker-compose.yml file:
* GITHUB_OAUTH: Github token with access to read the repository where the ontology is stored. This token will be used to download the modified files through the GitHub API. For more information, see [the official GitHub page about creating a personal access token](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line).
* WBAPI: Endpoint of the target Wikibase instance API where the ontology will be sincronized. E.g. https://hercules-demo.wiki.opencura.com/w/api.php
* WBSPARQL: SPARQL endpoint of the target wikibase. E.g. https://hercules-demo.wiki.opencura.com/query/sparql
* WBUSER: Username of the user that will perform the synchronization operation in the target wikibase.
* WBPASS: Password of the user defined by the username stated above.
* WEBHOOK_SECRET: Secret key of the webhook created in the previous step.

## Launching the app directly with Python
This application is compatible with Python 3.6 forwards, but the recommended Python version is at least Python 3.7 due to performance. After you have installed Python, you can run the following command to install every dependency:
```
pip install -r requirements.txt
```

After the requirements have been installed, you need to set directly the environment variables described in the previous section. After that, the following command can be executed to launch the app:
```
python wsgi.py
```

Alternatively, there is a sh script available that installs the dependencies and runs the server automatically. In order to execute this script, you have to set the environment variables and then run:
```
sh start_server.sh
```
