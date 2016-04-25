import numpy as np
from Queue import Queue
from collections import namedtuple
import logging
from Packet import Packet
from simenv import get_env

lognormal_param = namedtuple('lognormal_param', 'mean sigma')

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

        self.service_lognormal_param = None
        self.arrival_distributions = dict()

        self.__load_mpip_report()

        self.milc_timesteps = config['timesteps']
        self.current_milc_timestep = 0

    def tick(self):

        env = get_env()

        sim_complete = False

        while not self.current_milc_timestep <= self.milc_timesteps:

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

    def get_arrival_wait_time(self, host_id):
        return np.random.lognormal(mean=self.arrival_distributions[host_id].mean,
                                   sigma=self.arrival_distributions[host_id].sigma)

    def is_packet_waiting_for_service(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet that needs to be serviced
        """
        return self.service_queue[host_id].qsize() > 0

    def service_packet(self, host_id):
        pkt = self.service_queue[host_id].get()
        # todo: make note that this packet is done, generate new packets if needed.

    def get_service_wait_time(self, host_id):
        return np.random.lognormal(self.service_lognormal_param.mean, self.service_lognormal_param.sigma)

    def __load_mpip_report(self):

                # todo: read milc filepath from config file
        # for now just hardcode the sample

        with open('data/node4_sample/su3_rmd.128.9161.1.mpiP') as file:
            lines = [line.rstrip('\n') for line in file]

        avg_mean = 0.
        avg_sigma = 0.
        entry_count = 0

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
            if split[2].startswith('*'):  # the "all" line
                line_number += 1
                line = lines[line_number]
                continue
            rank = int(split[2])
            count = int(split[3])
            max = float(split[4])
            mean = float(split[5])
            min = float(split[6])
            app_percent = float(split[7])
            mpi_percent = float(split[8])

            # we are focusing on call site 2 for MPI_Isend and call site 11 for MPI_Allreduce
            if site not in [2, 11]:
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
            sigma = min  # NOT CORRECT!
            logging.info('%i %f', rank, sigma)

            avg_mean += mean
            avg_sigma += sigma
            entry_count += 1

            self.arrival_distributions[rank] = lognormal_param(mean, sigma)

        # we need to calculate the average mean and sigma to use for computation time
        self.service_lognormal_param = lognormal_param(avg_mean/entry_count, avg_sigma/entry_count)

        # done
