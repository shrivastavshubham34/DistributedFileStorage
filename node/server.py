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
import random
import greet_pb2
import greet_pb2_grpc
import network_manager_pb2
import network_manager_pb2_grpc

from node_position import NodePosition

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Greeter(greet_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        """
        This method will be remotely invoked by a node who wants to get added to the network
        """
        logger.info("SayHello invoked from {}".format(request.client_node_ip))
        globals.my_coordinates = globals.node_connections.connection_dict[NodePosition.CENTER].node_coordinates
        logger.debug("my_coordinates: {}".format(globals.my_coordinates))

        logger.debug("node_connections: {}".format(globals.node_connections.connection_dict))

        neighbor_pos_coord_dict = helper.get_neighbor_coordinates(globals.my_coordinates)
        logger.debug("neighbor_pos_coord_dict: {}".format(neighbor_pos_coord_dict))
        available_pos_coord_dict = {}
        unavailable_pos_coord_dict = {}

        for position in neighbor_pos_coord_dict.keys():
            if position in globals.node_connections.connection_dict.keys():
                unavailable_pos_coord_dict[position] = neighbor_pos_coord_dict[position]
            else:
                available_pos_coord_dict[position] = neighbor_pos_coord_dict[position]

        logger.debug("available_pos_coord_dict: {}".format(available_pos_coord_dict))
        logger.debug("unavailable_pos_coord_dict: {}".format(unavailable_pos_coord_dict))

        # TODO: if available_pos == 0 forward the request
        if len(available_pos_coord_dict) == 0:
            logger.debug("len(available_pos_coord_dict) == 0")
            return greet_pb2.HelloReply(message='Hello, %s!' % request.client_node_ip,
                                        client_node_coordinates=str(None),
                                        server_node_coordinates=str(globals.my_coordinates))

        # Find position/coordinates such that it creates a compact network structure
        # Check neighbor or neighbor's neighbor for deciding the position
        if len(available_pos_coord_dict) == 4:
            # All positions are available
            new_node_position = NodePosition.RIGHT  # default to right position
            new_node_coordinates = available_pos_coord_dict[new_node_position]

            # Add client to NodeConnections
            channel = grpc.insecure_channel(request.client_node_ip + ":" + str(globals.port))
            conn = connection.Connection(channel=channel,
                                         node_position=new_node_position,
                                         node_coordinates=new_node_coordinates,
                                         node_ip=request.client_node_ip)
            globals.node_connections.add_connection(conn)
            logger.debug("node_connections: {}".format(globals.node_connections.connection_dict))

            logger.debug("new_node_coordinates: {}".format(new_node_coordinates))
            logger.debug("additional_connections=[]")

            return greet_pb2.HelloReply(message='Hello, %s!' % request.client_node_ip,
                                        client_node_coordinates=str(new_node_coordinates),
                                        server_node_coordinates=str(globals.my_coordinates),
                                        additional_connections=str([]))

        # Eliminate the farthest position
        if len(available_pos_coord_dict) == 3:
            logger.debug("len(available_pos) == 3; available_pos_coord_dict: (before)".format(available_pos_coord_dict))
            if NodePosition.TOP in unavailable_pos_coord_dict \
                    and neighbor_pos_coord_dict[NodePosition.TOP] == unavailable_pos_coord_dict[NodePosition.TOP]:
                del available_pos_coord_dict[NodePosition.BOTTOM]
            elif NodePosition.BOTTOM in unavailable_pos_coord_dict \
                    and neighbor_pos_coord_dict[NodePosition.BOTTOM] == unavailable_pos_coord_dict[NodePosition.BOTTOM]:
                del available_pos_coord_dict[NodePosition.TOP]
            elif NodePosition.LEFT in unavailable_pos_coord_dict.keys() \
                    and neighbor_pos_coord_dict[NodePosition.LEFT] == unavailable_pos_coord_dict[NodePosition.LEFT]:
                del available_pos_coord_dict[NodePosition.RIGHT]
            elif NodePosition.RIGHT in unavailable_pos_coord_dict \
                    and neighbor_pos_coord_dict[NodePosition.RIGHT] == unavailable_pos_coord_dict[NodePosition.RIGHT]:
                del available_pos_coord_dict[NodePosition.LEFT]
            logger.debug("len(available_pos) == 3; available_pos_coord_dict: (after)".format(available_pos_coord_dict))

        new_node_position = None
        new_node_coordinates = None
        my_neighbors_neighbor_pos_coord = {}
        neighbor_coord_ip_dict = {}

        # Eliminate one more option
        if len(available_pos_coord_dict) == 2:
            logger.debug("len(available_pos) == 2; available_pos_coord_dict: (before) {}"
                         .format(available_pos_coord_dict))
            # Two options available - Left & Right or Top & Bottom
            for my_neighbor_position in unavailable_pos_coord_dict.keys():
                my_neighbor_coordinates = unavailable_pos_coord_dict[my_neighbor_position]  # tuple(x,y)
                my_neighbor_ip = globals.node_connections.connection_dict[my_neighbor_position].node_ip  # ip
                logger.debug("my_neighbor_coordinates: {}".format(my_neighbor_coordinates))
                logger.debug("my_neighbor_ip: {}".format(my_neighbor_ip))

                server_node_ip = my_neighbor_ip
                channel = grpc.insecure_channel(server_node_ip + ":" + str(globals.port))
                network_manager_stub = network_manager_pb2_grpc.NetworkManagerStub(channel)

                logger.debug("Calling GetNodeMetaData in {}".format(server_node_ip))
                response = network_manager_stub.GetNodeMetaData(network_manager_pb2.GetNodeMetaDataRequest(
                    client_node_ip=globals.my_ip))
                logger.debug("GetNodeMetaData response from {}: {}".format(server_node_ip, response))

                neighbor_coord_ip_dict = eval(response.server_coord_ip_dict)

                logger.debug("neighbor_coord_ip_dict: {}".format(neighbor_coord_ip_dict))

                # Check your neighbor's connections
                # Assign the same position as your neighbor's neighbor to the new node
                # L->L else R; T->T else B
                logger.debug("my_neighbor_coordinates: {}".format(my_neighbor_coordinates))
                my_neighbors_neighbor_pos_coord = helper.get_neighbor_coordinates(my_neighbor_coordinates)
                logger.debug("my_neighbors_neighbor_pos_coord: {}".format(my_neighbors_neighbor_pos_coord))

                if NodePosition.TOP in available_pos_coord_dict \
                        and my_neighbors_neighbor_pos_coord[NodePosition.TOP] in neighbor_coord_ip_dict \
                        and neighbor_coord_ip_dict[my_neighbors_neighbor_pos_coord[NodePosition.TOP]] != globals.my_ip:
                    new_node_position = NodePosition.TOP
                if NodePosition.BOTTOM in available_pos_coord_dict \
                        and my_neighbors_neighbor_pos_coord[NodePosition.BOTTOM] in neighbor_coord_ip_dict \
                        and neighbor_coord_ip_dict[my_neighbors_neighbor_pos_coord[NodePosition.BOTTOM]] != globals.my_ip:
                    new_node_position = NodePosition.BOTTOM
                if NodePosition.LEFT in available_pos_coord_dict \
                        and my_neighbors_neighbor_pos_coord[NodePosition.LEFT] in neighbor_coord_ip_dict \
                        and neighbor_coord_ip_dict[my_neighbors_neighbor_pos_coord[NodePosition.LEFT]] != globals.my_ip:
                    new_node_position = NodePosition.LEFT
                if NodePosition.RIGHT in available_pos_coord_dict \
                        and my_neighbors_neighbor_pos_coord[NodePosition.RIGHT] in neighbor_coord_ip_dict \
                        and neighbor_coord_ip_dict[my_neighbors_neighbor_pos_coord[NodePosition.RIGHT]] != globals.my_ip:
                    new_node_position = NodePosition.RIGHT

                if new_node_coordinates:
                    del available_pos_coord_dict[new_node_position]

                if new_node_position is not None:
                    new_node_coordinates = available_pos_coord_dict[new_node_position]
                    break

            logger.debug("new_node_coordinates: {}".format(new_node_coordinates))
            logger.debug("new_node_position: {}".format(new_node_position))
            logger.debug("len(available_pos) == 2; available_pos_coord_dict: (after) {}"
                         .format(available_pos_coord_dict))

        if new_node_coordinates is None:
            logger.info("new_node_coordinates == ():")
            # assign random position
            random_position = random.choice(list(available_pos_coord_dict.keys()))
            new_node_coordinates = available_pos_coord_dict[random_position]
            new_node_position = random_position
            logger.debug("new_node_coordinates: {}".format(new_node_coordinates))
            logger.debug("new_node_position: {}".format(new_node_position))

        # Assign node a position
        try:
            additional_connections = [neighbor_coord_ip_dict[my_neighbors_neighbor_pos_coord[new_node_position]]]
        except KeyError:
            additional_connections = []

        logger.info("additional_connections: {}".format(additional_connections))
        logger.info("new_node_coordinates: {}".format(new_node_coordinates))

        # Add new node to NodeConnections
        channel = grpc.insecure_channel(request.client_node_ip + ":" + str(globals.port))
        conn = connection.Connection(channel=channel,
                                     node_position=new_node_position,
                                     node_coordinates=new_node_coordinates,
                                     node_ip=request.client_node_ip)

        if not globals.node_connections.add_connection(conn):
            logger.debug("Node {} already in the network".format(request.client_node_ip))
            return greet_pb2.HelloReply(message='Hello, %s!' % request.client_node_ip,
                                        client_node_coordinates=str(None),
                                        server_node_coordinates=str(globals.my_coordinates))

        logger.info("node_connections: {}".format(globals.node_connections.connection_dict))

        # Send my position and the added node's position
        return greet_pb2.HelloReply(message='Hello, %s!' % request.client_node_ip,
                                    client_node_coordinates=str(new_node_coordinates),
                                    server_node_coordinates=str(globals.my_coordinates),
                                    additional_connections=str(additional_connections))
