import numpy as np
from Queue import Queue


class TrafficControllerSimulated:
    def __init__(self, config):

        self.arrival_rate = config['arrival_rate']

        self.service_rate = config['service_rate']
        self.sleep_alpha = config['sleep_alpha']

        self.packets_arrival = dict()
        self.packets_service = dict()
        for host_id in range(config['num_of_hosts']):
            self.packets_arrival[host_id] = Queue()
            self.packets_service[host_id] = Queue()

    def is_packet_waiting_for_arrival(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet waiting to 'arrive'
        """
        raise NotImplementedError()

    def receive_arrival_packet(self, host_id):
        """
        Request the next packet, Controller should remove from arrival_queue
        :param host_id: The id of the host requesting
        :return: None
        """
        raise NotImplementedError()

    def is_packet_waiting_for_service(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet that needs to be serviced
        """
        raise NotImplementedError()

    def service_packet(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: How long to service packet for
        """
        return np.random.exponential(scale=1. / self.service_rate)
