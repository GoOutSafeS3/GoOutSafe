#!/bin/sh
coverage run -m pytest
cp .coverage /coverage/.coverage