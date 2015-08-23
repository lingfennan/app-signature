#!/usr/bin/env bash
protoc --proto_path=./ --cpp_out=./ --java_out=./ --python_out=./ *.proto
