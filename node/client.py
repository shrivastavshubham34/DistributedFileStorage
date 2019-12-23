import os
import sys
import hashlib
import math
sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')

import globals
import connection
import grpc
import helper
import logging
import greet_pb2
import greet_pb2_grpc
import network_manager_pb2
import network_manager_pb2_grpc
import storage_pb2
import storage_pb2_grpc

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Client:

    @staticmethod
    def greet(server_node_ip):
        """
        This method is used to get connected/added to the network.
        :param server_node_ip: ip address of any node in the network.
        :return: None
        """
        logger.info("Connecting to {} at port {}...".format(server_node_ip, globals.port))
        channel = grpc.insecure_channel(server_node_ip + ":" + str(globals.port))
        greeter_stub = greet_pb2_grpc.GreeterStub(channel)
        response = greeter_stub.SayHello(greet_pb2.HelloRequest(client_node_ip=globals.my_ip))

        logger.info("Response from {}: {}".format(server_node_ip, response))
        if eval(response.client_node_coordinates) is None:
            logger.error("Cannot join {}. Maximum node connection capacity reached or node already in the network."
                         .format(server_node_ip))
            return

        # Get coordinates => tuple(x,y)
        globals.my_coordinates = eval(response.client_node_coordinates)

        # Add yourself to NodeConnections
        my_conn = connection.Connection(channel=None,
                                        node_position=globals.my_position,
                                        node_coordinates=globals.my_coordinates,
                                        node_ip=globals.my_ip)
        globals.node_connections.add_connection(my_conn)
        logger.debug("NodeConnections.connection_dict: {}".format(globals.node_connections.connection_dict))

        # Calculate server node's position
        server_node_coordinates = eval(response.server_node_coordinates)

        neighbor_pos_coord_dict = helper.get_neighbor_coordinates(globals.my_coordinates)
        logger.debug("neighbor_pos_coord_dict: {}".format(neighbor_pos_coord_dict))

        server_node_position = None
        for item in neighbor_pos_coord_dict.items():
            if item[1] == server_node_coordinates:
                server_node_position = item[0]  # eg.: NodePosition.TOP
                break
        logger.debug(("server_node_position: {}".format(server_node_position)))

        # Add server node to NodeConnections
        server_node_conn = connection.Connection(channel=channel,
                                                 node_position=server_node_position,
                                                 node_coordinates=server_node_coordinates,
                                                 node_ip=server_node_ip)
        globals.node_connections.add_connection(server_node_conn)
        logger.debug("node_connections: {}".format(globals.node_connections.connection_dict))

        additional_connections = eval(response.additional_connections)
        logger.debug("additional_connections: {}".format(additional_connections))

        # If the new node (this node) has neighbors then make additional connections with them
        for server_node_ip in additional_connections:
            logger.info("Making necessary additional connections...")
            channel = grpc.insecure_channel(server_node_ip + ":" + str(globals.port))
            logger.info("Connecting to {} at port {}...".format(server_node_ip, globals.port))

            logger.info("Informing new neighbors to form connections...")
            logger.debug("Calling rpc UpdateNeighborMetaData with args: client_node_ip {}, client_node_coordinates: {}"
                         .format(globals.my_ip, globals.my_coordinates))
            network_manager_stub = network_manager_pb2_grpc.NetworkManagerStub(channel)
            response = network_manager_stub.UpdateNeighborMetaData(
                network_manager_pb2.UpdateNeighborMetaDataRequest(client_node_ip=globals.my_ip,
                                                                  client_node_coordinates=str(globals.my_coordinates)))

            logger.info("Response from {}: {}".format(server_node_ip, response))

            server_node_coordinates = eval(response.server_node_coordinates)
            server_node_position = None
            for item in neighbor_pos_coord_dict.items():
                if item[1] == server_node_coordinates:
                    server_node_position = item[0]
                    break

            # Add server node to NodeConnections
            server_node_conn = connection.Connection(channel=channel,
                                                     node_position=server_node_position,
                                                     node_coordinates=server_node_coordinates,
                                                     node_ip=server_node_ip)
            globals.node_connections.add_connection(server_node_conn)
            logger.debug("node_connections: {}".format(globals.node_connections.connection_dict))
        logger.info("Node added to the network successfully...")
        logger.info("Node details: node_coordinates: {}, node_connections: {}"
                    .format(globals.node_connections.connection_dict[globals.my_position].node_coordinates,
                            globals.node_connections.connection_dict))


    @staticmethod
    def test_upload_data(server_node_ip):
        """
        This is a sample of the storage functionality from the client side. It currently sends data to only one node in
        in the mesh. The middleware or another team needs to figure out which node to send the data to.
        :param server_node_ip:
        :return: None
        """

        chunk_size_payload = 1024  # set chunk stream size of 1KB # globals.initial_page_memory_size_bytes
        logger.info("Connecting to {} at port {}...".format(server_node_ip, globals.port))
        channel = grpc.insecure_channel(server_node_ip + ":" + str(globals.port))
        memory_storage_stub = storage_pb2_grpc.FileServerStub(channel)


        logger.info("Node memory available in bytes: {}"
                    .format(memory_storage_stub.get_node_available_memory_bytes(storage_pb2.EmptyRequest()).bytes))

        # prepare message to save in memory (this can be a file too)
        message = "Hello my name is John".encode()
        logger.info("Attempting to upload message: {}".format(message))
        message_id = "122333"
        # create sample hash
        hash_id = hashlib.sha1(message_id.encode()).hexdigest()
        message_chunk_bytes = storage_pb2.ChunkRequest(chunk=message)

        metadata = (
            ('key-hash-id', hash_id),
            ('key-chunk-size', str(chunk_size_payload)),
        )

        # check if this hash is in memory already
        res = memory_storage_stub.is_hash_id_in_memory(storage_pb2.HashIdRequest(hash_id=hash_id))
        logger.info("Hash Exist in Node: {}".format(res.success)) # should not exist at the beginning

        # send message as a chunk
        res2 = memory_storage_stub.upload_single_chunk(message_chunk_bytes, metadata=metadata)
        logger.info("Was data uploaded {}".format(res2.success))
        res3 = memory_storage_stub.is_hash_id_in_memory(storage_pb2.HashIdRequest(hash_id=hash_id))
        logger.info("Hash Exist in Node: {}".format(res3.success)) # should exist at the beginning

        # download download the message just uploaded before
        stream_of_bytes_chunks_downloaded = \
            memory_storage_stub.download_chunk_stream(storage_pb2.HashIdRequest(hash_id=hash_id))
        logger.info("Download Results:")
        for chunk in stream_of_bytes_chunks_downloaded:
            logger.info(chunk.chunk)

        logger.info("Node memory available in bytes: {}"
                    .format(memory_storage_stub.get_node_available_memory_bytes(storage_pb2.EmptyRequest()).bytes))

        ## print all hashes saved in a server
        logger.info("Hashes saved so far: ")
        for hash_ in memory_storage_stub.get_stored_hashes_list_iterator(storage_pb2.EmptyRequest()):
            logger.info(hash_.hash_id)

        # send stream of chucks from a file
        def get_file_chunks(file_path, chunk_size):
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if len(chunk) == 0:
                        return
                    yield storage_pb2.ChunkRequest(chunk=chunk)

        def save_chunks_to_file(filename, chunks):
            with open("./" + filename, 'wb') as f:
                for chunk in chunks:
                    f.write(chunk.chunk)

        chunk_size_payload = 3 * 1024 * 1024 # set chunk stream size to 3MB
        file_path = "./docs/mesh.png"
        file_size_bytes = os.path.getsize(file_path)
        number_of_chunks = math.ceil(file_size_bytes / chunk_size_payload)
        is_replica = True

        metadata = (
            ('key-hash-id', hash_id),
            ('key-chunk-size', str(chunk_size_payload)),
            ('key-number-of-chunks', str(number_of_chunks)),
            ('key-is-replica', str(is_replica))
        )
        message_stream_of_chunk_bytes = get_file_chunks(file_path, chunk_size_payload)

        res4 = memory_storage_stub.upload_chunk_stream(message_stream_of_chunk_bytes, metadata=metadata)
        ("Was data uploaded {}".format(res4.success))

        # download file request
        stream_of_bytes_chunks_downloaded = memory_storage_stub.download_chunk_stream(storage_pb2.HashIdRequest(hash_id=hash_id))
        output_path = "docs/mesh_out.png"
        save_chunks_to_file(output_path, stream_of_bytes_chunks_downloaded)
