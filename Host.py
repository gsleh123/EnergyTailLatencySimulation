import logging
from simenv import get_env
import numpy as np
from Packet import Packet
from TrafficControllerSimulated import TrafficControllerSimulated
from TrafficControllerMilcSampled import TrafficControllerMilcSampled

hosts = []


def init_hosts(config):
    global hosts
    global num_of_hosts

    hosts = []
    num_of_hosts = config['num_of_hosts']

    if config['mpip_report_type'] == 'MILC':
        traffic_controller = TrafficControllerMilcSampled(config)
    else:
        traffic_controller = TrafficControllerSimulated(config)
    get_env().process(traffic_controller.tick())

    for i in range(num_of_hosts):
        hosts.append(Host(i, traffic_controller, config))
        get_env().process(hosts[i].packet_arrival())
        get_env().process(hosts[i].packet_service())
        get_env().process(hosts[i].logging(1))
        # get_env().process(Host.hosts[i].temp_tick())


def get_hosts():
    global hosts
    return hosts


class Host:
    def __init__(self, idd, traffic_controller, config):
        self.id = idd

        self.freq_lower_bound = config['freq_lower_bound']
        self.freq_upper_bound = config['freq_upper_bound']

        self.traffic_controller = traffic_controller

    def packet_arrival(self):
        env = get_env()

        while True:

            # wait until there's something to do
            while not self.traffic_controller.is_packet_waiting_for_arrival(self.id):
                # TODO: maybe keep track of waiting time
                yield env.timeout(1)
                continue

            # there is a packet. Service it.
            self.traffic_controller.receive_arrival_packet(self.id)

            logging.info('Packet arrived, time %i', env.now)

    def packet_service(self):
        env = get_env()

        while True:

            if not self.traffic_controller.is_packet_waiting_for_service(self.id):
                yield env.timeout(1)
                continue

            yield env.timeout(np.random.exponential(scale=1./2))

            self.traffic_controller.service_packet(self.id)

            logging.info('Packet processed, time %i', env.now)

    def logging(self, log_interval):
        env = get_env()

        while True:
            yield env.timeout(log_interval)

            logging.info('Host %i has %i packets in queue', self.id,
                         self.traffic_controller.service_queue[self.id].qsize())
