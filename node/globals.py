"""
Global variables file
"""

import threading
import machine_info
from node_connections import NodeConnections
from node_position import NodePosition

from storage_manager import StorageManagerServer

import hb_server

port = None
my_ip = None
my_position = None
my_coordinates = None
initial_node_memory_size_bytes = None
initial_page_memory_size_bytes = None
node_connections = None
whole_mesh_dict = None
lock = None
storage_object = None
nodes_for_replication = None
data_received_event = None
data_received = None


def init():
    """
    Definitions of global variables that are used across modules
    """
    global port, my_ip, my_position, my_coordinates, whole_mesh_dict, initial_node_memory_size_bytes, initial_page_memory_size_bytes, node_connections, lock, storage_object, data_received_event
    port = 2750
    my_ip = machine_info.get_my_ip()
    my_position = NodePosition.CENTER
    my_coordinates = None

    initial_node_memory_size_bytes = 1 * 1024 * 1024 * 1024  # start with 1 GB for storage
    initial_page_memory_size_bytes =  100 * 1024 # start with 100KB for storage
    whole_mesh_dict = hb_server.whole_mesh_dict
    node_connections = NodeConnections()
    lock = threading.Lock()
    storage_object = StorageManagerServer(initial_node_memory_size_bytes, initial_page_memory_size_bytes)
    data_received_event = threading.Event()