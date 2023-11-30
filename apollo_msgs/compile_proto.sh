# compile multiple protocol buffers at the same time
protoc -I=./ --python_out=./ ./apollo_modules/common_msgs/**/*.proto
