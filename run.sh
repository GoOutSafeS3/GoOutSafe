#!/bin/bash

export FLASK_APP="monolith/app.py:create_app"
#docker-compose build

if [[ "$1" == "local" ]]; then 
    docker-compose up local &
    flask run
elif [[ "$1" == "local-tests" ]]; then 
    docker-compose up local &
    pytest --cov=monolith --cov-report term-missing --cov-report html --html=report.html
elif [[ "$1" == "tests" ]]; then 
    docker-compose up tests
elif [[ "$1" == "monolith" ]]; then 
    docker-compose up monolith
else
    echo "Service not recognized"
fi;