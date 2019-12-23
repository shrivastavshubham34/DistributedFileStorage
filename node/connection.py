class Connection:
    """
    Stores connection information
    channel: gRPC channel
    node_position: One of the position from Enum (TOP/BOTTOM/LEFT/RIGHT)
    node_coordinates: tuple containing x & y coordinates
    """
    def __init__(self, channel, node_position, node_coordinates, node_ip):
        self._channel = channel
        self._node_position = node_position
        self._node_coordinates = node_coordinates
        self._node_ip = node_ip

    @property
    def channel(self):
        return self._channel

    @property
    def node_position(self):
        return self._node_position

    @property
    def node_coordinates(self):
        return self._node_coordinates\

    @property
    def node_ip(self):
        return self._node_ip
