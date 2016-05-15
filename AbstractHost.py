import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
from Packet import Packet
import Host


def Abstract_Runner(target_timestep):
    env = get_env()

    while env.now < target_timestep:
        yield env.timeout(1)
        logging.info('Sim Time: %i' % env.now)


class AbstractHost:
    def __init__(self, hostid, config, arrival_distribution, arrival_kwargs, service_distribution, service_kwargs,
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
        self.id = hostid
        self.arrival_dist = arrival_distribution
        self.arrival_kwargs = arrival_kwargs
        self.service_dist = service_distribution
        self.service_kwargs = service_kwargs
        self.send_to = send_to
        self.should_generate = should_generate
        self.problem_type = config['Abstract']['problem_type']

        self.packets = Queue()

        # data collection
        self.packet_latency = list()

    def process_arrivals(self):
        env = get_env()

        while True:
            if self.should_generate:
                yield env.timeout(self.arrival_dist(**self.arrival_kwargs))
                self.packets.put(Packet(env.now))
                logging.info('Host %i generated a packet' % self.id)
            else:
                yield env.timeout(1)

    def process_service(self):
        env = get_env()

        while True:
            if self.packets.qsize() == 0:
                yield env.timeout(0.1)
                continue

            yield env.timeout(self.service_dist(**self.service_kwargs))
            pkt = self.packets.get()
            logging.info('Host %i serviced a packet' % self.id)

            # if not last destination, send onward
            if len(self.send_to) > 0:

                if self.problem_type == 1:
                    host_destination = Host.get_hosts()[np.random.choice(self.send_to)]
                    # todo: communication time
                    host_destination.packets.put(pkt)
                    logging.info('Host %i sent packet to host %i' % (self.id, host_destination.id))
                elif self.problem_type == 2:
                    for hostindex in self.send_to:
                        host_destination = Host.get_hosts()[hostindex]
                        # todo: communication time
                        host_destination.packets.put(pkt)
                        logging.info('Host %i sent packet to host %i' % (self.id, host_destination.id))

            # if last destination, log it
            else:
                full_processing_time = env.now - pkt.birth_tick
                self.packet_latency.append(full_processing_time)
                logging.info('Host %i finished packet. time spent: %f' % (self.id, full_processing_time))
