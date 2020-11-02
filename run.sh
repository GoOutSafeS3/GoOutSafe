#!/bin/bash

export FLASK_APP="monolith/app.py:create_app"
docker-compose build

if [[ "$1" == "local" ]]; then 
    docker-compose up local &
    flask run
elif [[ "$1" == "local-tests" ]]; then 
    docker-compose up local &
    pytest --cov=monolith --cov-report term-missing --cov-report html --html=report.html
elif [[ "$1" == "tests" ]]; then 
    docker-compose up --exit-code-from tests tests
elif [[ "$1" == "monolith-test" ]]; then 
    docker-compose up monolith
elif [[ "$1" == "monolith-prod" ]]; then 
    docker-compose -f docker-compose.yml up monolith
else
    echo "Service not recognized"
fi;