echo $1

protoc \
  -I=$1 \
  -I=$1/openscenario_msgs \
   --python_out=$1 $1/openscenario_msgs/*.proto
