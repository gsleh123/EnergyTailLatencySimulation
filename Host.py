import logging
from Queue import Queue
import numpy as np

from simenv import get_env
from Packet import Packet

hosts = []


def init_hosts(num, arrival_rate, service_rate, sleep_alpha, freq_lower_bound, freq_upper_bound):
    global hosts
    global num_of_hosts

    hosts = []
    num_of_hosts = num

    for i in range(num_of_hosts):
        hosts.append(Host(i, arrival_rate, service_rate, sleep_alpha, freq_lower_bound, freq_upper_bound))
        get_env().process(hosts[i].packet_arrival())
        get_env().process(hosts[i].packet_service())
        get_env().process(hosts[i].logging(1))
        # get_env().process(Host.hosts[i].temp_tick())


def get_hosts():
    global hosts
    return hosts


class Host:

    def __init__(self, id, arrival_rate, service_rate, sleep_alpha, freq_lower_bound, freq_upper_bound):
        self.id = id
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.sleep_alpha = sleep_alpha

        self.packets = Queue()

    def packet_arrival(self):
        env = get_env()

        while True:
            yield env.timeout(np.random.exponential(scale=1./self.arrival_rate))

            # 1 / arrival_rate as input into exponential

            logging.info('Packet arrived, time %i', env.now)

            self.packets.put(Packet())

    def packet_service(self):
        env = get_env()

        while True:

            if self.packets.empty():
                yield env.timeout(1)
                continue

            yield env.timeout(np.random.exponential(scale=1./self.service_rate))
            self.packets.get()

            logging.info('Packet processed, time %i', env.now)

    def logging(self, log_interval):
        env = get_env()

        while True:
            yield env.timeout(log_interval)

            logging.info('Host %i has %i packets in queue', self.id, self.packets.qsize())


