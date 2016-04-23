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

        self.__load_mpip_report()
        # todo: that...For now just use a preset distribution
        # self.arrival_distributions = dict()
        # lognormal_param = namedtuple('lognormal_param', 'mean sigma')
        # for host_id in range(config['num_of_hosts']):
        #     self.arrival_distributions[host_id] = lognormal_param(5, 0.5)

    def tick(self):

        env = get_env()

        while True:

            # todo: check if any hosts have completed a 'cycle'

            # testing
            for host_id in range(len(self.arrival_queue)):
                if np.random.sample() > 0.2:
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
        Called when host wants to tell the controller it has finished servicing a packet
        :param host_id: The id of the host requesting
        :return:
        """
        pkt = self.service_queue[host_id].get()
        # todo: make note that this packet is done, generate new packets if needed.

    def __load_mpip_report(self):
        lognormal_param = namedtuple('lognormal_param', 'mean sigma')

        with open('node4_sample/su3_rmd.128.9161.1.mpiP') as file:
            lines = [line.rstrip('\n') for line in file]

        line_number = 0
        line = lines[line_number]
        while not line.startswith('@--- Callsite Time statistics'):
            line_number += 1
            line = lines[line_number]

        # now we are at the callsite stats. finish skipping the header
        line_number += 3
        line = lines[line_number]  # this is the first callsite line
        while not line.startswith('-'):

            split = line.split()  # whitespace is default

            if len(line) < 2 or len(split) < 8:
                line_number += 1
                line = lines[line_number]
                continue

            mpi_call_type = split[0]
            site = int(split[1])
            rank = int(split[2])
            count = int(split[3])
            max = float(split[4])
            mean = float(split[5])
            min = float(split[6])
            app_percent = float(split[7])
            mpi_percent = float(split[8])

            # we are focusing on call site 2 for MPI_Isend and call site 11 for MPI_Allreduce
            if site is not 2 or site is not 11:
                line_number += 1
                line = lines[line_number]
                continue

            if site is 2:  # MPI_ISend
                pass
            elif site is 11:  # MPI_Allreduce
                pass  # todo

            line_number += 1
            line = lines[line_number]

            # try to estimate the lognormal distribution's sigma, given the max, min as 95%.
            sigma = (max - min) / 4  # NOT CORRECT!

            self.arrival_distributions[rank] = lognormal_param(mean, sigma)
