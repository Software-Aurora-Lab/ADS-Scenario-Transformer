# compile multiple protocol buffers at the same time

find ./ -type f -name '*.proto' -exec sed -i 's|import "modules/common_msgs/|import "apollo_msgs/|g' {} +


protoc \
  -I=/home/runner/ADS-scenario-transfer \
  -I=/home/runner/ADS-scenario-transfer/apollo_msgs \
  -I=/home/runner/ADS-scenario-transfer/apollo_msgs/basic_msgs \
  -I=/home/runner/ADS-scenario-transfer/apollo_msgs/localization_msgs \
  -I=/home/runner/ADS-scenario-transfer/apollo_msgs/map_msgs \
  -I=/home/runner/ADS-scenario-transfer/apollo_msgs/routing_msgs \
  --python_out=/home/runner/ADS-scenario-transfer \
  /home/runner/ADS-scenario-transfer/apollo_msgs/basic_msgs/*.proto \
  /home/runner/ADS-scenario-transfer/apollo_msgs/localization_msgs/*.proto \
  /home/runner/ADS-scenario-transfer/apollo_msgs/map_msgs/*.proto \
  /home/runner/ADS-scenario-transfer/apollo_msgs/routing_msgs/*.proto