import logging

from simenv import get_env
from Packet import Packet
from TrafficController import TrafficController

hosts = []


def init_hosts(num, arrival_rate, service_rate, sleep_alpha, freq_lower_bound, freq_upper_bound,
               computation_communication_ratio, mpip_report_type):
    global hosts
    global num_of_hosts

    hosts = []
    num_of_hosts = num

    for i in range(num_of_hosts):
        hosts.append(Host(i, TrafficController(arrival_rate, service_rate, sleep_alpha,
                                               computation_communication_ratio, mpip_report_type),
                          freq_lower_bound, freq_upper_bound))
        get_env().process(hosts[i].packet_arrival())
        get_env().process(hosts[i].packet_service())
        get_env().process(hosts[i].logging(1))
        # get_env().process(Host.hosts[i].temp_tick())


def get_hosts():
    global hosts
    return hosts


class Host:
    def __init__(self, idd, traffic_controller, freq_lower_bound, freq_upper_bound):
        self.id = idd

        self.freq_lower_bound = freq_lower_bound
        self.freq_upper_bound = freq_upper_bound

        self.traffic_controller = traffic_controller

    def packet_arrival(self):
        env = get_env()

        while True:

            # wait until there's something to do
            while self.traffic_controller.queue_arrivals_empty():
                # TODO: maybe keep track of waiting time
                yield env.timeout(1)
                continue

            yield env.timeout(self.traffic_controller.next_incoming())

            logging.info('Packet arrived, time %i', env.now)

            self.packets.put(Packet())

    def packet_service(self):
        env = get_env()

        while True:

            if self.packets.empty():
                yield env.timeout(1)
                continue

            yield env.timeout()
            self.packets.get()

            logging.info('Packet processed, time %i', env.now)

    def logging(self, log_interval):
        env = get_env()

        while True:
            yield env.timeout(log_interval)

            logging.info('Host %i has %i packets in queue', self.id, self.packets.qsize())
