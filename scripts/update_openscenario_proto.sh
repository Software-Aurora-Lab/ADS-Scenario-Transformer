#!/bin/bash

# Run this script at the project_root
PROJECT_ROOT=$(pwd)

path="$PROJECT_ROOT/openscenario_msgs"

poetry remove openscenario-msgs
sh $path/compile_proto.sh
poetry add $path