import logging
from simenv import get_env
import numpy as np
from Packet import Packet
from Queue import Queue
import Host

MILC_TIMESTEP = 0


class MILCHost:
    def __init__(self, idd, config, arrival_distributions, service_lognormal_param):
        self.id = idd

        self.target_timestep = config['timesteps']

        # self.freq_lower_bound = config['freq_lower_bound']
        # self.freq_upper_bound = config['freq_upper_bound']

        # for testing, just 1 neighbor for now
        if self.id < 4:
            self.neighbors = range(4)
        else:
            self.neighbors = range(4, 8)
        print self.id, 'my neighbors', self.neighbors

        # distributions to sample with
        self.comm_mean = arrival_distributions[self.id].mean
        self.comm_sigma = arrival_distributions[self.id].sigma
        self.comp_mean = service_lognormal_param.mean
        self.comp_sigma = service_lognormal_param.sigma

        self.received_packet_count_for_cycle = 0

        # special counter for host 0 which is the reciever of the AllReduce
        if idd == 0:
            self.all_reduce_receive_count = 0

    def process(self):
        global MILC_TIMESTEP
        env = get_env()

        hosts = Host.get_hosts()

        while MILC_TIMESTEP <= self.target_timestep:

            if self.id == 0:
                print 'Starting timestep', MILC_TIMESTEP

            current_timestep = MILC_TIMESTEP

            # send out packets
            for i in range(len(self.neighbors)):
                yield env.timeout(np.random.lognormal(mean=self.comm_mean, sigma=self.comm_sigma))
                if self.id == 0:
                    pass
                hosts[self.neighbors[i]].received_packet_count_for_cycle += 1

            while self.received_packet_count_for_cycle < len(self.neighbors):
                yield env.timeout(0.01)

            print self.id, 'Done communicating'

            # we have received all the packets from our neighbors. Do some computation
            yield env.timeout(np.random.lognormal(mean=self.comp_mean, sigma=self.comp_sigma))

            # Computation done. Do the MPI_AllReduce call by sending a packet to host/rank 0
            yield env.timeout(np.random.lognormal(mean=self.comm_mean, sigma=self.comm_sigma))
            hosts[0].all_reduce_receive_count += 1

            # Done with cycle
            # reset own counters
            self.received_packet_count_for_cycle = 0

            if self.id != 0:
                # wait around for timestep to change
                while MILC_TIMESTEP == current_timestep:
                    yield env.timeout(0.01)
            else:
                # for host 0
                while self.all_reduce_receive_count != len(hosts):
                    yield env.timeout(0.01)

                # we have recieved all the AllReduce packets. Do some computation on it
                yield env.timeout(np.random.lognormal(mean=self.comp_mean, sigma=self.comp_sigma))

                # mimic sending back the data
                yield env.timeout(np.random.lognormal(mean=self.comm_mean, sigma=self.comm_sigma))

                # reset the allreduce counter
                self.all_reduce_receive_count = 0

                # change the MILC_TIMESTEP
                MILC_TIMESTEP += 1
