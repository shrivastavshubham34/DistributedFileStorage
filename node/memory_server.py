import grpc
from concurrent import futures
import os
import sys

sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')

import rumour_pb2
import rumour_pb2_grpc
import machine_info
import hb_server

class RumourServicer(rumour_pb2_grpc.RumourServicer):
    def sendMemoryData(self, request, context):
        print("in receive")
        return rumour_pb2.MemoryStatsReply(cpu_usage=machine_info.get_my_cpu_usage(),
                                           memory_usage=machine_info.get_my_memory_usage(),
                                           disk_usage=machine_info.get_my_disk_usage())

    def sendLogicalMesh(self,request,context):
        print("in send")
        return rumour_pb2.LogicalMeshReply(wholemesh=str(hb_server.whole_mesh_dict))


def sendmemory():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rumour_pb2_grpc.add_RumourServicer_to_server(RumourServicer(), server)
    server.add_insecure_port('[::]:50061')
    server.start()
    print("Server starting...")
    server.wait_for_termination()