import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
import Host

MILC_TIMESTEP = 0
MILC_COMP_CYCLES_PER_TIMESTEP = 4

SIMPY_WAIT_RESOLUTION = 0.05

def MILC_Runner(target_timestep):
    global MILC_TIMESTEP
    env = get_env()

    while MILC_TIMESTEP <= target_timestep:
        yield env.timeout(1)


class MILCHost:
    def __init__(self, idd, config, isend_distributions, allreduce_distributions, service_lognormal_param,
                 dimension, dimension_to_host):
        self.id = idd
        self.dimension = dimension

        self.target_timestep = config['timesteps']

        # self.freq_lower_bound = config['freq_lower_bound']
        # self.freq_upper_bound = config['freq_upper_bound']

        self.neighbors = []
        self.__figure_out_neighbors(dimension_to_host, config['MILC']['dimensions'])

        print self.id, 'my neighbors', self.neighbors

        # distributions to sample with
        self.allreduce_mean = allreduce_distributions[self.id].mean
        self.allreduce_sigma = allreduce_distributions[self.id].sigma
        self.isend_mean = isend_distributions[self.id].mean
        self.isend_sigma = isend_distributions[self.id].sigma
        self.comp_mean = service_lognormal_param.mean
        self.comp_sigma = service_lognormal_param.sigma

        self.received_packet_count_for_cycle = [0] * MILC_COMP_CYCLES_PER_TIMESTEP

        # special counter for host 0 which is the reciever of the AllReduce
        if idd == 0:
            self.all_reduce_receive_count = 0

    def __figure_out_neighbors(self, dimension_to_host, problem_size):
        neighbor_indicies = [None]*4
        for i in range(4):
            neighbor_indicies[i] = self.__neighbor_dimension_helper(i, problem_size)

        self.neighbors.append(dimension_to_host[
                                  self.dimension[0], self.dimension[1], self.dimension[2], neighbor_indicies[3][0]
                              ])
        self.neighbors.append(dimension_to_host[
                                  self.dimension[0], self.dimension[1], self.dimension[2], neighbor_indicies[3][1]
                              ])

        self.neighbors.append(dimension_to_host[
                                  self.dimension[0], self.dimension[1], neighbor_indicies[2][0], self.dimension[3]
                              ])
        self.neighbors.append(dimension_to_host[
                                  self.dimension[0], self.dimension[1], neighbor_indicies[2][1], self.dimension[3]
                              ])

        self.neighbors.append(dimension_to_host[
                                  self.dimension[0], neighbor_indicies[1][0], self.dimension[2], self.dimension[3]
                              ])
        self.neighbors.append(dimension_to_host[
                                  self.dimension[0], neighbor_indicies[1][1], self.dimension[2], self.dimension[3]
                              ])

        self.neighbors.append(dimension_to_host[
                                  neighbor_indicies[0][0], self.dimension[1], self.dimension[2], self.dimension[3]
                              ])
        self.neighbors.append(dimension_to_host[
                                  neighbor_indicies[0][1], self.dimension[1], self.dimension[2], self.dimension[3]
                              ])

        self.neighbors = self.neighbors

    def __neighbor_dimension_helper(self, dimension_index, problem_size):
        """
        Figure out the neighbor's indicies for a particular dimension
        :param dimension_index: dimension (0-3)
        :param problem_size: Size of problem, for bounds
        :return: Array of size 2 holding indicies for neighbors
        """

        my_val = self.dimension[dimension_index]

        dimension_max = problem_size[dimension_index]

        if my_val == 0:
            return [dimension_max-1, 1]
        elif my_val == dimension_max-1:
            return [my_val - 1, 0]
        else:
            return [my_val - 1, my_val + 1]

    def process(self):
        global MILC_TIMESTEP
        env = get_env()

        hosts = Host.get_hosts()

        while MILC_TIMESTEP <= self.target_timestep:

            if self.id == 0:
                print 'Starting timestep', MILC_TIMESTEP

            current_timestep = MILC_TIMESTEP

            # loop a few times, not sure how many MILC does.
            for l in range(MILC_COMP_CYCLES_PER_TIMESTEP):
                # send out packets
                for i in range(len(self.neighbors)):
                    yield env.timeout(np.random.lognormal(mean=self.isend_mean, sigma=self.isend_sigma))
                    if self.id == 0:
                        pass
                    hosts[self.neighbors[i]].received_packet_count_for_cycle[l] += 1

                while self.received_packet_count_for_cycle[l] < len(self.neighbors):
                    yield env.timeout(SIMPY_WAIT_RESOLUTION)

                # we have received all the packets from our neighbors. Do some computation
                yield env.timeout(np.random.lognormal(mean=self.comp_mean, sigma=self.comp_sigma))

            # Computation done. Do the MPI_AllReduce call by sending a packet to host/rank 0
            yield env.timeout(np.random.lognormal(mean=self.allreduce_mean, sigma=self.allreduce_sigma))
            hosts[0].all_reduce_receive_count += 1

            # Done with cycle
            # reset own counters
            self.received_packet_count_for_cycle = [0] * MILC_COMP_CYCLES_PER_TIMESTEP

            if self.id != 0:
                # wait around for timestep to change
                while MILC_TIMESTEP == current_timestep:
                    yield env.timeout(SIMPY_WAIT_RESOLUTION)
            else:
                # for host 0
                while self.all_reduce_receive_count != len(hosts):
                    yield env.timeout(SIMPY_WAIT_RESOLUTION)

                # we have recieved all the AllReduce packets. Do some computation on it
                yield env.timeout(np.random.lognormal(mean=self.comp_mean, sigma=self.comp_sigma))

                # mimic sending back the data
                yield env.timeout(np.random.lognormal(mean=self.allreduce_mean, sigma=self.allreduce_sigma))

                # reset the allreduce counter
                self.all_reduce_receive_count = 0

                # change the MILC_TIMESTEP
                MILC_TIMESTEP += 1
