#!/bin/sh
rm .coverage -f
coverage run -m pytest
RESULT=$?
cp .coverage /coverage/.coverage
exit $RESULT