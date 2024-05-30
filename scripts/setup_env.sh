#!/bin/bash

# Make sure to run this script at the root of the project
project_path=$(pwd)

if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source $project_path/venv/bin/activate
    export PYTHONPATH=$project_path/venv/lib/python3.10/dist-packages:$PYTHONPATH
else
    python3 -m venv venv
    source $project_path/venv/bin/activate
    export PYTHONPATH=$project_path/venv/lib/python3.10/dist-packages:$PYTHONPATH
fi

echo "PYTHONPATH is now set to: $PYTHONPATH"

pip install poetry
poetry install