import grpc
import globals
import logging
import os
import time
from node_position import NodePosition

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Pulse:
    @staticmethod
    def check_neighbor_node_pulse():
        """
        Checks for neighbor nodes' pulse
        """
        while True:
            for item in list(globals.node_connections.connection_dict.items()):
                if item[0] == NodePosition.CENTER:
                    continue

                tries = 0
                while tries < 3:
                    try:
                        grpc.channel_ready_future(item[1].channel).result(timeout=1)
                        if os.system("ping -c 1 " + item[1].node_ip):
                            logger.info("{} pulse failed. Check your physical connection".format(item[1].node_ip))
                            tries += 1
                            continue
                    except grpc.FutureTimeoutError:
                        logger.info("{} pulse failed. Check if your node process is active".format(item[1].node_ip))
                        tries += 1
                        continue
                    break
                    time.sleep(1)

                if tries == 3:
                    logger.info("Removing {} from the network".format(item[1].node_ip))
                    globals.node_connections.remove_connection(item[0])

            time.sleep(1)
