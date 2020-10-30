#!/bin/sh
coverage run -m pytest
coverage xml -o /coverage/coverage.xml