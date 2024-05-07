#!/bin/bash

if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    python3 -m venv .venv
    source .venv/bin/activate
    pip install poetry
    poetry install    
fi

export PYTHONPATH=/home/sora/Desktop/changnam/ADS-scenario-transfer/.venv/lib/python3.10/dist-packages

