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
    """
    :type packets: Queue.Queue of Packet
    :type problem_type: int
    """
    def __init__(self, hostid, config, arrival_distribution, arrival_kwargs, comm_distribution, comm_kwargs,
                 comp_time, send_to, should_generate):
        """
        :param arrival_distribution: function to generate arrival wait times from
        :param arrival_kwargs: keyword arguments to feed into the arrival distribution
        :param comm_distribution: function to generate service wait times from
        :param comm_kwargs: keyword arguments to feed into the arrival distribution
        :param comp_time: Fixed time to spend computing
        :param send_to: list of hosts to randomly send packets done servicing to
        :param should_generate: should the host generate its own packets
        :return:
        """
        self.id = hostid
        self.arrival_dist = arrival_distribution
        self.arrival_kwargs = arrival_kwargs
        self.comm_dist = comm_distribution
        self.comm_kwargs = comm_kwargs
        self.comp_time = comp_time
        self.send_to = send_to
        self.should_generate = should_generate
        self.problem_type = config['Abstract']['problem_type']

        self.packets = Queue()

        # Problem-specific variables

        # For problem 3, gather, we keep track via a dict of queues, indexed by hostid
        if self.problem_type == 3 and self.id == 0:
            self.packets_gather = dict()
            for i in range(1, config['host_count']):
                self.packets_gather[i] = Queue()

        # data collection
        self.packet_latency = list()

    def process_arrivals(self):
        env = get_env()

        while True:
            if self.should_generate:
                yield env.timeout(self.arrival_dist(**self.arrival_kwargs))
                pkt = Packet(env.now, self.id)
                self.packets.put(pkt)
                logging.info('Host %i generated a packet' % self.id)
            else:
                yield env.timeout(1)

    def process_service(self):
        env = get_env()

        while True:

            if self.problem_type != 3 or self.id != 0:
                if self.packets.qsize() == 0:
                    yield env.timeout(0.1)
                    continue
            else:
                # problem type 3, host 0

                # other hosts still add packets to our self.packets structure
                # transfer them to the queue dict
                while self.packets.qsize() > 0:
                    p = self.packets.get()
                    self.packets_gather[p.last_parent].put(p)

                can_gather = not any(q.empty() for q in self.packets_gather.itervalues())
                if not can_gather:
                    yield env.timeout(1)
                    continue

            # yield env.timeout(self.service_dist(**self.service_kwargs))
            yield env.timeout(self.comp_time)

            if self.problem_type != 3 or self.id != 0:
                pkt = self.packets.get()
                logging.info('Host %i serviced a packet' % self.id)

                # if not last destination, send onward
                if len(self.send_to) > 0:

                    pkt.last_parent = self.id

                    if self.problem_type in [1, 3]:
                        host_destination = Host.get_hosts()[np.random.choice(self.send_to)]

                        comm_time = self.comm_dist(**self.comm_kwargs)
                        logging.info('Host %i waiting for %f for computation' % (self.id, comm_time))
                        yield env.timeout(comm_time)

                        host_destination.packets.put(pkt)
                        logging.info('Host %i sent packet to host %i' % (self.id, host_destination.id))
                    elif self.problem_type == 2:
                        for hostindex in self.send_to:
                            host_destination = Host.get_hosts()[hostindex]

                            yield env.timeout(self.comm_dist(**self.comm_kwargs))

                            host_destination.packets.put(pkt)
                            logging.info('Host %i sent packet to host %i' % (self.id, host_destination.id))

                # if last destination, log it
                else:
                    self.finish_packet(env, pkt)
            else:  # problem 3
                logging.info('Host %i has gathered and serviced a set' % self.id)
                pkts = [q.get(block=False) for q in self.packets_gather.itervalues()]
                for pkt in pkts:
                    self.finish_packet(env, pkt)

    def finish_packet(self, env, pkt):
        full_processing_time = env.now - pkt.birth_tick
        self.packet_latency.append(full_processing_time)
        logging.info('Host %i finished packet. time spent: %f' % (self.id, full_processing_time))
