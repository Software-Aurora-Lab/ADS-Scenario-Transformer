# compile multiple protocol buffers at the same time

# find ./ -type f -name '*.proto' -exec sed -i 's|import "modules/common_msgs/|import "apollo_msgs/|g' {} +

# Set the local variable path
path="/Users/changnam/dev/ADS/q4/ADS-scenario-transfer"

# Run protoc compiler
protoc \
  -I="$path" \
  -I="$path/apollo_msgs" \
  -I="$path/apollo_msgs/basic_msgs" \
  -I="$path/apollo_msgs/localization_msgs" \
  -I="$path/apollo_msgs/map_msgs" \
  -I="$path/apollo_msgs/routing_msgs" \
  -I="$path/apollo_msgs/perception_msgs" \
  --python_out="$path" \
  "$path/apollo_msgs/basic_msgs"/*.proto \
  "$path/apollo_msgs/localization_msgs"/*.proto \
  "$path/apollo_msgs/map_msgs"/*.proto \
  "$path/apollo_msgs/routing_msgs"/*.proto \
  "$path/apollo_msgs/perception_msgs"/*.proto