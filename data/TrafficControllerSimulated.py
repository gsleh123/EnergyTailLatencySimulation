import numpy as np
from Queue import Queue


class TrafficController:
    def __init__(self, config):

        self.arrival_rate = config['arrival_rate']

        self.service_rate = config['service_rate']
        self.sleep_alpha = config['sleep_alpha']

        self.packets_arrival = Queue()

    def queue_arrivals_empty(self):
        return self.packets_arrival.qsize() == 0

    def next_incoming(self):
        """
        Request the next packet
        :return:
        """
        return self.true_next_incoming()

    def service_packet(self):
        """
        :return: How long to service packet for
        """
        return np.random.exponential(scale=1. / self.service_rate)
