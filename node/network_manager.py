import os
import sys
sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')

import globals
import connection
import grpc
import helper
import logging
import network_manager_pb2
import network_manager_pb2_grpc

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NetworkManager(network_manager_pb2_grpc.NetworkManagerServicer):

    def GetNodeMetaData(self, request, context):
        """
        This method is invoked by client to get information about this node's neighbors
        """
        logger.info("GetNodeMetaData invoked from " + request.client_node_ip)
        server_coord_ip_dict = {}
        for conn in globals.node_connections.connection_dict.values():
            server_coord_ip_dict[conn.node_coordinates] = conn.node_ip

        logger.debug("server_node_meta_dict: {}".format(server_coord_ip_dict))
        return network_manager_pb2.GetNodeMetaDataResponse(server_coord_ip_dict=str(server_coord_ip_dict))

    def UpdateNeighborMetaData(self, request, context):
        """
        This method is invoked by client to inform that the node is a new neighbor
        """
        logger.info("UpdateNeighborMetaData invoked from {}: {}"
                    .format(request.client_node_ip, request.client_node_coordinates))
        neighbor_pos_coord_dict = helper.get_neighbor_coordinates(globals.my_coordinates)
        logger.debug("neighbor_pos_coord_dict: {}".format(neighbor_pos_coord_dict))

        client_node_coordinates = eval(request.client_node_coordinates)

        new_neighbor_position = None
        for item in neighbor_pos_coord_dict.items():
            if item[1] == client_node_coordinates:
                new_neighbor_position = item[0]
                break

        # Add new neighbor to NodeConnections
        channel = grpc.insecure_channel(request.client_node_ip + ":" + str(globals.port))
        conn = connection.Connection(channel=channel,
                                     node_position=new_neighbor_position,
                                     node_coordinates=client_node_coordinates,
                                     node_ip=request.client_node_ip)
        globals.node_connections.add_connection(conn)
        logger.debug("node_connections: {}".format(globals.node_connections.connection_dict))

        return network_manager_pb2.UpdateNeighborMetaDataResponse(server_node_coordinates=str(globals.my_coordinates))
