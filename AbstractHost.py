import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
from Packet import Packet
import Host

ABSTRACT_TIMESTEP = 0

def Abstract_Runner(target_timestep):
    global ABSTRACT_TIMESTEP

    env = get_env()

    while ABSTRACT_TIMESTEP < target_timestep:
        yield env.timeout(1)


class AbstractHost:
    def __init__(self, arrival_distribution, arrival_kwargs, service_distribution, service_kwargs,
                 send_to, should_generate):
        """
        :param arrival_distribution: function to generate arrival wait times from
        :param arrival_kwargs: keyword arguments to feed into the arrival distribution
        :param service_distribution: function to generate service wait times from
        :param service_kwargs: keyword arguments to feed into the arrival distribution
        :param send_to: list of hosts to randomly send packets done servicing to
        :param should_generate: should the host generate its own packets
        :return:
        """
        self.arrival_dist = arrival_distribution
        self.arrival_kwargs = arrival_kwargs
        self.service_dist = service_distribution
        self.service_kwargs = service_kwargs
        self.send_to = send_to
        self.should_generate = should_generate

        self.packets = Queue()

        # data collection
        self.packet_latency = list()

    def process_arrivals(self):
        env = get_env()

        while True:
            if self.should_generate:
                yield env.timeout(self.arrival_dist(self.arrival_kwargs))
                self.packets.put(Packet(env.now))

    def process_service(self):
        env = get_env()

        while True:
            if self.packets.qsize() == 0:
                yield env.timeout(0.01)
                continue

            yield env.timeout(self.service_dist(self.service_kwargs))
            pkt = self.packets.get()

            # if not last destination, send onward
            if len(self.send_to) > 0:
                host_destination = np.random.choice(Host.get_hosts())
                host_destination.packets.put(pkt)
            # if last destination, log it
            else:
                full_processing_time = env.now - pkt.birth_tick
                self.packet_latency.append(full_processing_time)
