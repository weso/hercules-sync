#!/bin/bash

export FLASK_ENV=production

app="ontology_sync"
docker build -t ${app} .
docker run -d -p 5000:5000 ${app}
