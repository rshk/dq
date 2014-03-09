#!/bin/bash
exec py.test -vvv -rfEsxX --cov=dq --cov-report=term-missing --pep8 "$@"
