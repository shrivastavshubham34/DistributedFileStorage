#!/bin/bash

mkdir -p -- "./node/generated/"

if ! [[ -x "$(command -v python3)" ]];
then
    python -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/greet.proto

    python -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/machine_stats.proto

    python -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/network_manager.proto

    python -m grpc_tools.protoc -I./protos --python_out=./node/generated \
            --grpc_python_out=./node/generated ./protos/traversal.proto

    python -m grpc_tools.protoc -I./protos --python_out=./node/generated \
            --grpc_python_out=./node/generated ./protos/rumour.proto

    python -m grpc_tools.protoc -I./protos --python_out=./node/generated \
            --grpc_python_out=./node/generated ./protos/replication.proto
else
    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/greet.proto

    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/machine_stats.proto

    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/network_manager.proto

    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/traversal.proto

    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
        --grpc_python_out=./node/generated ./protos/storage.proto

    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
            --grpc_python_out=./node/generated ./protos/rumour.proto

    python3 -m grpc_tools.protoc -I./protos --python_out=./node/generated \
            --grpc_python_out=./node/generated ./protos/replication.proto
fi
