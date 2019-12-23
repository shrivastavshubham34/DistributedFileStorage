import grpc
from concurrent import futures
import os
import sys
import logging
sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
import globals
import rumour_pb2
import rumour_pb2_grpc

logging.basicConfig(filename='hb_server.log', filemode='w',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
whole_mesh_dict = {}
heartbeat_meta_dict = {}

def updatehearbeatdict(newnodeheartbeatdict):
    for node in newnodeheartbeatdict:
        if node in heartbeat_meta_dict:
            heartbeat_meta_dict[node] = max(heartbeat_meta_dict[node], newnodeheartbeatdict[node])
        else:
            heartbeat_meta_dict[node] = newnodeheartbeatdict[node]

def updatemeshdict(newnodemeshdict):
    #print("new node mesh....")
    #print(newnodemeshdict)
    for node in newnodemeshdict:
        if node not in whole_mesh_dict:
            whole_mesh_dict[node] = newnodemeshdict[node]
        else:
            if whole_mesh_dict[node] != newnodemeshdict[node]:
                whole_mesh_dict[node] = newnodemeshdict[node]

class RumourServicer(rumour_pb2_grpc.RumourServicer):
    def sendheartbeat (self, request, context):
        #print("in receive", request)
        response = request #fetch request here
        if  response.pos in whole_mesh_dict and response.ip != whole_mesh_dict[response.pos]:
            heartbeat_meta_dict.remove(response.pos+"-"+whole_mesh_dict[response.pos])
            whole_mesh_dict[response.pos] = response.ip
            heartbeat_meta_dict[response.pos+"-"+response.ip] = response.heartbeatcount

        newnodemeshdict = eval(response.wholemesh)
        newnodeheartbeatdict = eval(response.heartbeatdict)
        updatehearbeatdict(newnodeheartbeatdict)
        if newnodemeshdict:
            updatemeshdict(newnodemeshdict)

        return rumour_pb2.HeartBeatReply()

def hb_serve():
    logger.info(globals.my_ip)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rumour_pb2_grpc.add_RumourServicer_to_server(RumourServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server starting...")
    server.wait_for_termination()