# compile multiple protocol buffers at the same time
protoc -I=./ --python_out=./generated_common_msgs ./modules/common_msgs/**/*.proto
