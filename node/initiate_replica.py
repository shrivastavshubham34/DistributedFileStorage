import json
import socket
import globals
def start_replica():
    # get node self IP
    serverAddressPort = (globals.my_ip, 21000)
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    print("INSIDE GOSSIP", serverAddressPort)
    dict = {}
    message = json.dumps({"IPaddress": globals.my_ip, "gossip": False, "Dictionary": dict, "BlackListedNodes": []})
    UDPClientSocket.sendto(message.encode(), serverAddressPort)