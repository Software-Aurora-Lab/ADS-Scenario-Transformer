#!/bin/bash

# Set the root directory of your project
project_root="./apollo_modules"

# Find all .proto files and modify import statements
find "$project_root" -type f -name "*.proto" -exec sed -i.bak 's/import "modules\//import "apollo_modules\//g' {} \;

# Remove the backup files
find "$project_root" -type f -name "*.bak" -delete