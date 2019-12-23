import grpc
import os
import sys

sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')

import rumour_pb2
import rumour_pb2_grpc


if __name__ == "__main__":
    channel = grpc.insecure_channel('localhost:50061')
    rumour_stub = rumour_pb2_grpc.RumourStub(channel)
    print(rumour_stub)
    response = rumour_stub.sendLogicalMesh(rumour_pb2.LogicalMeshRequest())
    print(response)