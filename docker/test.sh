#!/bin/sh
rm .coverage -f
coverage run -m pytest
cp .coverage /coverage/.coverage