import os
import sys
import time
from threading import Thread
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

sys.path.append("../" + os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/utils/')
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/generated/')

import storage_pb2, storage_pb2_grpc
from memory_manager import MemoryManager
from initiate_replica import start_replica
from replicate_data import replication
from replicate_data import get_best_path
import globals

DEBUG = 0

class StorageManagerServer(storage_pb2_grpc.FileServerServicer):

    def __init__(self, memory_node_bytes, page_memory_size_bytes):
        self.memory_manager = MemoryManager(memory_node_bytes, page_memory_size_bytes)

    def replicate_data(self, message_stream_of_chunk_bytes, metadata):
        start_replica()
        time.sleep(5)
        print("GLOBALS --", globals.nodes_for_replication)
        list_of_neigbors = []
        for item in globals.node_connections.connection_dict.items():
            if item[1].node_ip != globals.my_ip and item[1].node_ip not in list_of_neigbors:
                list_of_neigbors.append(item[1].node_ip)
        nodes = list_of_neigbors
        if len(nodes) > 0:
            path_one = get_best_path(globals.whole_mesh_dict, nodes[0])
            status_one = replication(path_one, message_stream_of_chunk_bytes, metadata)
            #path_two = get_best_path(globals.whole_mesh_dict, nodes[1])
            #status_two = replication(path_two, message_stream_of_chunk_bytes, metadata)
            print("First Replication Status ", status_one)
            #print("Second Replication Status ", status_two)
        else:
            print("No nodes for replication")

    def upload_chunk_stream(self, request_iterator, context):
        print("WHOLE MESH DICT =", globals.whole_mesh_dict)
        hash_id = ""
        chunk_size = 0
        number_of_chunks = 0
        is_replica = "True"

        for key, value in context.invocation_metadata():
            if key == "key-hash-id":
                hash_id = value
            elif key == "key-chunk-size":
                chunk_size = int(value)
            elif key == "key-number-of-chunks":
                number_of_chunks = int(value)
            elif key == "key-is-replica":
                is_replica = str(value)

        assert hash_id != ""
        assert chunk_size != 0
        assert number_of_chunks != 0
        assert is_replica != ""
        success = self.memory_manager.put_data(request_iterator, hash_id, chunk_size, number_of_chunks, False)
        if is_replica != "False":
            replMetadata = {
                'key-hash-id': hash_id,
                'key-chunk-size': str(chunk_size),
                'key-number-of-chunks': str(number_of_chunks),
                'key-is-replica': is_replica
            }

            message_stream_of_chunk_bytes = self.memory_manager.get_data(hash_id)
            Thread(target=self.replicate_data, args=(message_stream_of_chunk_bytes, replMetadata)).start()

        return storage_pb2.ResponseBoolean(success=success)

    def upload_single_chunk(self, request_chunk, context):
        """
        :param request_chunk: single storage_pb2.ChunkRequest
        :param context: must include 'key-hash-id' and 'key-chunk-size' in metadata
        :return: boolean as storage_pb2.ResponseBoolean
        """
        hash_id = ""
        chunk_size = 0

        for key, value in context.invocation_metadata():
            if key == "key-hash-id":
                hash_id = value
            elif key == "key-chunk-size":
                chunk_size = int(value)

        assert hash_id != ""
        assert chunk_size != 0

        success = self.memory_manager.put_data(request_chunk, hash_id, chunk_size, 1, True)
        return storage_pb2.ResponseBoolean(success=success)

    def download_chunk_stream(self, request, context):
        """
        :param request: hash_id as storage_pb2.HashIdRequest(hash_id=hash_id)
        :param context: None
        :return: stream of storage_pb2.ChunkRequest
        """
        chunks = self.memory_manager.get_data(request.hash_id)
        for c in chunks:
            yield storage_pb2.ChunkRequest(chunk=c)

    def get_node_available_memory_bytes(self, request, context):
        """
        :param request: storage_pb2.EmptyRequest()
        :param context: None
        :return: double value as storage_pb2.ResponseDouble
        """
        bytes_ = self.memory_manager.get_available_memory_bytes()
        return storage_pb2.ResponseDouble(bytes=bytes_)

    def get_stored_hashes_list_iterator(self, request, context):
        """
        :param request: storage_pb2.EmptyRequest()
        :param context: None
        :return: stream of storage_pb2.storage_pb2.ResponseString
        """
        list_of_hashes = self.memory_manager.get_stored_hashes_list()
        for hash_ in list_of_hashes:
            yield storage_pb2.ResponseString(hash_id=hash_)

    def is_hash_id_in_memory(self, request, context):
        """
        :param request: storage_pb2.HashIdRequest(hash_id=hash_id)
        :param context: None
        :return: boolean as storage_pb2.ResponseBoolean
        """
        hash_exists = self.memory_manager.hash_id_exists(request.hash_id)
        return storage_pb2.ResponseBoolean(success=hash_exists)

    def is_hash_id_in_memory_non_rpc(self, hash_id):
        """
        :param hash_id: input string
        :return: hash_id found in memory as boolean
        """
        return self.memory_manager.hash_id_exists(hash_id)

    def download_list_of_data_chunks_non_rpc(self, hash_id):
        """
        :param hash_id: input string
        :return: list of data chunks
        """
        return self.memory_manager.get_data(hash_id)

    # def upload_chunk_stream_non_rpc(self, request_iterator, hash_id, chunk_size, number_of_chunks):
    #     success = self.memory_manager.put_data(request_iterator, hash_id, chunk_size, number_of_chunks, False)
    #     return success

