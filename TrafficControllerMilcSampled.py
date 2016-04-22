import numpy as np
from Queue import Queue
from collections import namedtuple
from Packet import Packet
from simenv import get_env


class TrafficControllerMilcSampled:
    """
    An abstract class for different control schemes
    The packets are always kept with the Controller, never given to the hosts
    Note: Not using abc module, just skeleton functions
    """
    def __init__(self, config):

        self.arrival_queue = dict()
        self.service_queue = dict()
        for host_id in range(config['num_of_hosts']):
            self.arrival_queue[host_id] = Queue()
            self.service_queue[host_id] = Queue()

        # todo: read milc filepath from config file
        # for now just hardcode the sample
        # todo: that...For now just use a preset distribution
        self.arrival_distributions = dict()
        lognormal_param = namedtuple('lognormal_param', 'mean sigma')
        for host_id in range(config['num_of_hosts']):
            self.arrival_distributions[host_id] = lognormal_param(5, 0.5)

    def tick(self):

        env = get_env()

        while True:

            # todo: check if any hosts have completed a 'cycle'

            # testing
            for host_id in range(len(self.arrival_queue)):
                if np.random.sample() > 0.6:
                    self.arrival_queue[host_id].put(Packet())

            yield env.timeout(1)

    def is_packet_waiting_for_arrival(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet waiting to 'arrive'
        """
        return self.arrival_queue[host_id].qsize() > 0

    def receive_arrival_packet(self, host_id):
        """
        Request the next packet, Controller should remove from arrival_queue
        :param host_id: The id of the host requesting
        :return: None
        """
        pkt = self.arrival_queue[host_id].get()
        self.service_queue[host_id].put(pkt)

    def is_packet_waiting_for_service(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet that needs to be serviced
        """
        return self.service_queue[host_id].qsize() > 0

    def service_packet(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: How long to service packet for
        """
        pkt = self.service_queue[host_id].get()
        # todo: make note that this packet is done, generate new packets if needed.
