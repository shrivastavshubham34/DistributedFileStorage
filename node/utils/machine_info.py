"""Information about the host machine"""

import socket
from psutil import cpu_percent, virtual_memory, disk_usage


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.0.0.0', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()

    return IP


def get_my_cpu_usage():
    return cpu_percent(interval=5)


def get_my_memory_usage():
    return virtual_memory().available


def get_my_disk_usage():
    return disk_usage("/").free
