#!/bin/bash

# Set the input Protocol Buffers file
input_file="openscenario_all.proto"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
  echo "Error: Input file $input_file not found."
  exit 1
fi

# Create a directory to store individual message files
output_dir="message_files"
mkdir -p "$output_dir"

# Use awk to extract each message definition and create a separate file
awk -v output_dir="$output_dir" '
  BEGIN {
    RS = "";   # Treat paragraphs as records
    FS = "\n";  # Treat lines as fields
    syntax_line = "syntax = \"proto2\";";
    package_line = "package openscenairo;";
  }
  {
    for (i = 1; i <= NF; i++) {
      if ($i ~ /^message/) {
        message_name = $i;
        sub(/^message /, "", message_name);
        sub(/ {/, "", message_name);
        file_name = output_dir "/" message_name ".proto";
        print syntax_line > file_name;   # Write syntax directive
        print package_line >> file_name; # Append package directive
        # Append the entire message content, including the closing curly brace
        print $0 >> file_name;
        print "File created:", file_name;
      }
    }
  }
' "$input_file"

echo "Individual message files have been created in $output_dir"

