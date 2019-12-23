import os
import sys
from queue import PriorityQueue
sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')

import globals
import logging
import random
import traversal_pb2
import traversal_pb2_grpc
import time
import threading
from queue import *
import grpc

from traversal_response_status import TraversalResponseStatus

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
gossip_dictionary = {"10.0.0.3": (10,10), "10.0.0.10": (10,11), "10.0.0.4": (11,10), "10.0.0.31": (11,11), "10.0.0.32": (12,11)}
q = PriorityQueue()

# up, left, right, down movements
row = [-1, 0, 0, 1]
col = [0, -1, 1, 0]

# source coordinates (1,0)
source_x = 0
source_y = 1

# destination coordinates (9,10)
destination_x = 3
destination_y = 5

# XXX
def find_data(hash_id):
    return random.choice([True, False])


# XXX
def fetch_data(hash_id):
    return "data"

# Nodes for shortest path
class Node:
    def __init__(self, x, y, w, parent):
        self.x = x
        self.y = y
        self.dist = w
        self.parent = parent

# XXX
class Traversal(traversal_pb2_grpc.TraversalServicer):
    def ReceiveData(self, request, context):
        logger.info("Traversal.ReceiveData hash_id:{} request_id:{} visited:{}"
                    .format(request.hash_id, request.request_id, request.visited))
        # print("Traversal.ReceiveData hash_id:{} request_id:{} visited:{}"
        #             .format(request.hash_id, request.request_id, request.visited))
        print("came hereeeeeee")
        data_found = globals.storage_object.is_hash_id_in_memory_non_rpc(request.hash_id)
        # Check if the file exits on current node
        if data_found:
            channel = grpc.insecure_channel(request.requesting_node_ip + ":" + str(globals.port))
            traversal_stub = traversal_pb2_grpc.TraversalStub(channel)
            chunks_list = globals.storage_object.download_list_of_data_chunks_non_rpc(request.hash_id)
            logger.debug("SendData: chunk: {}".format(chunks_list))

            for c in chunks_list:
                yield traversal_stub.SendData(traversal_pb2.SendDataRequest(
                    file_bytes=c,
                    request_id=request.request_id, client_node_ip=globals.my_ip))

            #    curr_data = fetch_data(request.hash_id)
            #    curr_mesh = self.create_logical_mesh()
            #    curr_path = self.find_shortest_path(curr_mesh)
            #    self.forward_response_data(curr_data, request.request_id, "", traversal_pb2.ReceiveDataResponse.TraversalResponseStatus.FOUND,
            #                               curr_path)
            # #    RespondData(file_bytes=curr_data, request_id=request.request_id, node_ip = request.node_ip, status = traversal_response_status.FOUND, path = curr_path)
            #    return traversal_pb2.ReceiveDataResponse(status=traversal_pb2.ReceiveDataResponse.TraversalResponseStatus.FOUND)

        # If file not found in node
        visited_ip = eval(request.visited)

        globals.data_received_event.clear()

        if globals.my_ip not in visited_ip:
            visited_ip.append(globals.my_ip)

        logger.info("Traversal.ReceiveData: visited: {}".format(visited_ip))
        neighbor_conn_list = []

        for item in globals.node_connections.connection_dict.items():
            neighbor_conn_list.append(item[1])

        forward_conn_list = []

        for neighbor_conn in neighbor_conn_list:
            logger.debug("visited_ip: {}".format(visited_ip))
            if neighbor_conn.node_ip not in visited_ip:
                logger.debug("Adding {} in visited_ip and forward_conn_list".format(neighbor_conn.node_ip))
                visited_ip.append(neighbor_conn.node_ip)
                forward_conn_list.append(neighbor_conn)

        print("Forwarded List: {}".format([conn.node_ip for conn in forward_conn_list]))
        print("Neighbor List: {}".format([conn.node_ip for conn in neighbor_conn_list]))
        print("Visited List: {}".format(visited_ip))

        logger.info("Forwarded List: {}".format([conn.node_ip for conn in forward_conn_list]))
        logger.info("Neighbor List: {}".format([conn.node_ip for conn in neighbor_conn_list]))
        logger.info("Visited List: {}".format(visited_ip))

        threading_list = []
        for forward_conn in forward_conn_list:
            forward_node_ip = forward_conn.node_ip #confirm
            channel = forward_conn.channel #confirm
            logger.debug("Forwarded Node IP: {}".format(forward_node_ip))
        #    print("Channel: {}".format(channel))
            forward_request_thread = threading.Thread(target=self.forward_receive_data_request,
                                                      args=(forward_node_ip, channel, request, visited_ip,
                                                            request.requesting_node_ip))
            threading_list.append(forward_request_thread)

        for thread in threading_list:
            thread.start()
            #thread.join()

        while not globals.data_received_event.is_set():
            # wait for data
            time.sleep(0.1)


       # return traversal_pb2.ReceiveDataResponse(
       #     status=traversal_pb2.ReceiveDataResponse.TraversalResponseStatus.FORWARDED) # confirm indentation

        logger.debug("Response: {}".format(globals.data_received))
        logger.debug("Return")
        #for chunk in globals.data_received:
        logger.debug("ReceiveDataRespnse: chunk: {}".format(globals.data_received))
        for c in globals.data_received:
            yield traversal_pb2.ReceiveDataResponse(
                status=traversal_pb2.ReceiveDataResponse.TraversalResponseStatus.FOUND, file_bytes=c)

    def RespondData(self, request, context):
        t = threading.Thread(target=self.forward_response_data, args=(request.file_bytes, request.request_id, request.node_ip, request.status, request.path))
        t.start()
        return traversal_pb2.ResponseDataResponse(
            status=traversal_pb2.ResponseDataResponse.TraversalResponseStatus.FORWARDED)



    #XXX
    def forward_receive_data_request(self, node_ip, channel, request, visited_ip, requesting_node_ip):
        logger.info("forward_receive_data_request: node_ip: {}".format(node_ip))

        traversal_stub = traversal_pb2_grpc.TraversalStub(channel)
        response = traversal_stub.ReceiveData(
            traversal_pb2.ReceiveDataRequest(
                                hash_id=str(request.hash_id),
                                request_id=str(request.request_id),
                                stack="",
                                visited=str(visited_ip),
                                requesting_node_ip=requesting_node_ip))
        logger.info("forward_receive_data_request: response: {}".format(response))
        return response

    def forward_response_data(self, file_bytes, request_id, node_ip, status, path):
        curr_path = eval(path)
        curr_coordinates = curr_path.pop()
        
        #check if data reached the initial invoking node
        if curr_path.empty():
            return file_bytes
        
        #get the channel through which the data will be propogated
        for item in globals.node_connections.connection_dict.items():
            if item[1].node_coordinates == curr_coordinates:
                channel = item[1].channel
                break
        
        #check if channel is alive. if not, update the 2D matrix and calculate a new shortest path
        if not channel.isAlive():
            mesh = self.create_logical_mesh()
            mesh[curr_coordinates[0]][curr_coordinates[1]] = 0
            curr_path = self.find_shortest_path(mesh)
            self.forward_response_data(file_bytes, request_id, node_ip, status, curr_path)

        #forward the request
        traversal_stub = traversal_pb2_grpc.TraversalStub(channel)
        response = traversal_stub.RespondData(
            traversal_pb2.RespondDataRequest(
                file_bytes=file_bytes,
                request_id=request_id,
                node_ip=node_ip,
                status=status,
                path=curr_path
            ))
        logger.info("Current response is: response : {}".format(response))
        return response


    #creating a 2D matrix to keep track of live and dead nodes
    def create_logical_mesh(self):
        min_row = list(gossip_dictionary.values())[0][0]
        min_col = list(gossip_dictionary.values())[0][1]
        max_row = list(gossip_dictionary.values())[len(gossip_dictionary)-1][0]
        max_col = list(gossip_dictionary.values())[len(gossip_dictionary)-1][1]

        for key in gossip_dictionary:
            if gossip_dictionary[key][0] < min_row:
                min_row = gossip_dictionary[key][0]
            if gossip_dictionary[key][1] < min_col:
                min_col = gossip_dictionary[key][1]
            if gossip_dictionary[key][0] > max_row:
                max_row = gossip_dictionary[key][0]
            if gossip_dictionary[key][1] > max_col:
                max_col = gossip_dictionary[key][1]

        cols = max_col - min_col + 1
        rows = max_row - min_col + 1

        mesh = [[0]*cols]*rows
        
        value_list = list(gossip_dictionary.values())
        for item in value_list:
            mesh[item[0]][item[1]] = 1
        logger.info("Current mesh is: mesh : {}".format(mesh))
        return mesh

    def find_shortest_path(self, mesh):
        path = []
        # M is total number of rows in matrix, N is total number of columns in matrix
        M = len(mesh)
        N = len(mesh[0])
        node = self.shortestDistance(mesh)

        if node != None:
            print("The shortest safe path has length of ", node.dist, "\nCoordinates of the path are :\n")
            path = self.printPath(node)
        else:
            print("No route is safe to reach destination")
        return path

    def isSafe(self, field, visited, x, y):
        return field[x][y] == 1 and not visited[x][y]

    def isValid(self, x, y, mesh):
        M = len(mesh)
        N = len(mesh[0])
        return x < M and y < N and x >= 0 and y >= 0

    def BFS(self, mesh):
        # created a visited list of Dimensions M*N that stores if a cell is visited or not
        visited = []
        M = len(mesh)
        N = len(mesh[0])
        m = 0
        while m < M:
            visited_row = [False] * N
            visited.append(visited_row)
            m += 1

        # create an empty queue
        q = Queue()
        # put source coodinates in the queue

        q.put(Node(source_x, source_y, 0, None))
        # run till queue is not empty
        while q.qsize() > 0:
            node = q.get()
            # pop front node from queue and process it
            i = node.x
            j = node.y
            dist = node.dist
            # if destination is found, return minimum distance
            if i == destination_x and j == destination_y:
                return node
            # check for all 4 possible movements from current cell and enqueue each valid movement
            k = 0
            while k < 4:
                # Skip if location is invalid or visited or unsafe
                # print("in BFS" , i + row[k], j + col[k])
                if self.isValid(i + row[k], j + col[k], mesh) and self.isSafe(mesh, visited, i + row[k], j + col[k]):
                    # mark it visited & push it into queue with +1 distance
                    visited[i + row[k]][j + col[k]] = True
                    q.put(Node(i + row[k], j + col[k], dist + 1, node))
                k += 1
        return None


    # Find Shortest Path from first column to last column in given field
    def shortestDistance(self, mesh):
        # update the mesh
        i = 0
        M = len(mesh)
        N = len(mesh[0])
        while i < M:
            j = 0
            while j < N:
                if mesh[i][j] == float('inf'):
                    mesh[i][j] = 0
                j += 1
            i += 1

        # call BFS and return shortest distance found by it
        return self.BFS(mesh)


    def printPath(self, node):
        if not node:
            return
        self.printPath(node.parent)
        co_ords = (node.x, node.y)
        path = []
        path.append(co_ords)
        return path
    # print("{", node.x, node.y, "}")

    def SendData(self, request, context):
        logger.info("SendData invoked from {}".format(request.client_node_ip))
        logger.debug("filebytes {}, request_id {}, client_node_ip {}".format(request.file_bytes, request.request_id,
                                                                             request.client_node_ip))

        globals.data_received = request.file_bytes

        globals.data_received_event.set()

        logger.info("Event set {}".format(globals.data_received))

        return traversal_pb2.SendDataResponse()

