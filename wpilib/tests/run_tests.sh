#!/bin/bash -e

cd $(dirname $0)

abspath() {
	echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# Not strictly necessary if testing-requirements was installed...
export PYTHONPATH=$(abspath ./..):$(abspath ../../hal-sim):$(abspath ../../hal-base)

if [ "$RUNCOVERAGE" == "1" ]; then
    python3 -m coverage run --source wpilib -m pytest "$@"
    python3 -m coverage report -m
else
    python3 -m pytest "$@"
fi

unset PYTHONPATH

# Run tests on examples repository
if [ "$CONTINUOUS_INTEGRATION" == "true" ]; then
    cd ../..
    curl https://raw.githubusercontent.com/robotpy/examples/master/_remote_tests.sh | bash -s base
fi

# Check for PEP 8

pycodestyle wpilib/wpilib --count --ignore=E402,E501,E265,E722,E741,E121,E123,E126,E133,E226,E241,E242,E704,W503,W292
