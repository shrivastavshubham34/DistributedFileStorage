import sys
import os
import grpc

sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')

import replication_pb2
import replication_pb2_grpc
import globals
class ReplicationService(replication_pb2_grpc.FileserviceServicer):

    def ReplicateFile(self, request, context):
        hash_id = ""
        chunk_size = 0
        number_of_chunks = 0
        is_replica = False

        for key, value in context.invocation_metadata():
            if key == "key-hash-id":
                hash_id = value
            elif key == "key-chunk-size":
                chunk_size = int(value)
            elif key == "key-number-of-chunks":
                number_of_chunks = int(value)
            elif key == "key-is-replica":
                is_replica = str(value)
        metadata = (
            ('key-hash-id', hash_id),
            ('key-chunk-size', str(chunk_size)),
            ('key-number-of-chunks', str(number_of_chunks)),
            ('key-is-replica', str(is_replica))
        )
        print("request = ", request.shortest_path[request.currentpos])
        list_of_neigbors = {}
        forward_coordinates = request.shortest_path[request.currentpos]
        for item in globals.node_connections.connection_dict.items():
            if item[1].node_ip != globals.my_ip and item[1].node_ip not in list_of_neigbors:
                list_of_neigbors[str(item[1].node_coordinates)] = item[1].node_ip
        if request.currentpos == len(request.shortest_path)-1 and request.currentpos > 0:
            #cache.saveVClock(str(request), str(request))
            #write_to_memory
            #status = globals.storage_object.upload_chunk_stream_non_rpc(request.bytearray, hash_id, chunk_size, number_of_chunks)
            return replication_pb2.ack(success=True, message="Data Replicated from "+globals.my_ip)
        else:
            forward_coordinates = request.shortest_path[request.currentpos+1]
            print("forward coord =", forward_coordinates)
            print(list_of_neigbors)
            print(list_of_neigbors[str(forward_coordinates)])
            forward_server_addr = list_of_neigbors[forward_coordinates]
            print("forward IP =", forward_server_addr)
            forward_server_addr= str(forward_server_addr)
            forward_port = globals.port
            #forward_channel = grpc.insecure_channel(forward_server_addr)
            forward_channel = grpc.insecure_channel(forward_server_addr + ":" + str(forward_port))
            print("FORWARD CHANNEL = ", forward_channel)
            forward_stub = replication_pb2_grpc.FileserviceStub(forward_channel)
            print("CALLED")
            updated_request = replication_pb2.FileData(initialReplicaServer=request.initialReplicaServer,
                                               bytearray=request.bytearray,
                                               vClock=request.vClock, shortest_path=request.shortest_path, currentpos=request.currentpos + 1)
            print("CALLED-2")
            forward_resp = forward_stub.ReplicateFile(updated_request, metadata = metadata)
            print("CALLED-03")
            print("forward_resp", forward_resp)
            return replication_pb2.ack(success=True, message="Data Forwarded to "+ forward_server_addr)