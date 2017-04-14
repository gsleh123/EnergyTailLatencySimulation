import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
from Packet import Packet
import Host
import sys

def Abstract_Runner(target_timestep):
    env = get_env()

    while env.now < target_timestep:
        yield env.timeout(1)
        logging.info('Sim Time: %i' % env.now)

    logging.info('Host Queue lengths after simulation:')
    for host in Host.get_hosts():
        queue_size = host.packets.qsize()
        if hasattr(host, 'packets_gather'):
            for q in host.packets_gather.values():
                queue_size += q.qsize()

        logging.debug('Host %i: %i' % (host.id, queue_size))


class AbstractHost:
    """
    :type packets: Queue.Queue of Packet
    :type problem_type: int
    """
    def __init__(self, hostid, config, arrival_distribution, arrival_kwargs, comm_distribution, comm_kwargs,
                 comp_time, send_to, should_generate, control_scheme):
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

        # region DVFS
        self.freq = config['freq_start']
        self.min_freq = config['freq_lower_bound']
        self.max_freq = config['freq_upper_bound']
        # endregion

        # region control scheme
        self.control_scheme = control_scheme
        # adjust_freq_on_arrival is called on packet  or arrival to change the frequency
        if control_scheme == 'basic':
            self.adjust_freq_on_arrival = self.arrival_basic
        elif control_scheme == 'back_propagate':
            self.adjust_freq_on_arrival = self.arrival_back_propagate
        else:
            self.adjust_freq_on_arrival = self.arrival_default_scheme

        # adjust_freq_after_send is called after a packet is sent to another host
        # takes the sent packet and host destination as arguments
        if control_scheme == 'basic':
            self.adjust_freq_after_send = self.after_send_default_scheme
        elif control_scheme == 'back_propagate':
            # note: only works from problem 3 -- gather -- right now
            self.adjust_freq_after_send = self.after_send_back_propagate
        else:
            self.adjust_freq_after_send = self.after_send_default_scheme

        # endregion

        self.packets = Queue()

        # region Problem-specific variables
        if self.problem_type == 3:
            self.receivers = list()
            self.packets_gather = dict()

        # endregion Problem-specific Variables

        # data collection
        self.packet_latency = list()
        self.queue_size = dict()
        self.freq_history = list()

    def process_arrivals(self):
        env = get_env()

        while True:

            # change frequency as required
            self.adjust_freq_on_arrival()

            if self.should_generate:
                time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
                yield env.timeout(time_till_next_packet_arrival)
                pkt = Packet(env.now, self.id)
                self.packets.put(pkt)
                logging.info('Host %i generated a packet %i after %f time' % (self.id, pkt.id, time_till_next_packet_arrival))
            else:
                yield env.timeout(0.1)

    def process_service(self):
        env = get_env()

        while True:

            if self.problem_type != 3:
                if self.packets.qsize() == 0:
                    yield env.timeout(0.1)
                    continue
            else:
                # problem type 3, host 0

                # other hosts still add packets to our self.packets structure
                # transfer them to the queue dict
                while self.packets.qsize() > 0:
                    p = self.packets.get()

                    if p.last_parent not in self.packets_gather:
                        pass

                    self.packets_gather[p.last_parent].put(p)

                can_gather = not any(q.empty() for q in self.packets_gather.itervalues())
                if not can_gather:
                    yield env.timeout(1)
                    continue
			
			# interp basically takes an x coordinate and looks at available x and y coordinates 
			# to determine the y coordinate using linear fit
            comp_time = np.interp(self.freq, [self.min_freq, self.max_freq],
                                   [self.comp_time, self.comp_time * (self.min_freq / self.max_freq) * (1.0/self.freq)])

            logging.info('Host %i waiting %f for computation' % (self.id, comp_time))
            yield env.timeout(comp_time)

            if self.problem_type != 3:
                pkt = self.packets.get()
                logging.info('Host %i serviced a packet %i' % (self.id, pkt.id))
                # if not last destination, send onward
                if len(self.send_to) > 0:

                    pkt.last_parent = self.id

                    if self.problem_type == 2:
                        comm_time = self.comm_dist(**self.comm_kwargs)

                        yield env.timeout(comm_time)
                        logging.info("Host %i finished communication for packet %i after %f time" % (self.id, pkt.id, comm_time))

                        for hostindex in self.send_to:
                            host_destination = Host.get_hosts()[hostindex]
                            host_destination.packets.put(pkt)
                            logging.info('Host %i sent packet %i to host %i' % (self.id, pkt.id, host_destination.id))
                    else:
                        logging.error("Problem type currently not supported")
                        sys.exit(1)

                # if last destination, log it
                else:
                    self.finish_packet(env, pkt)
            else:  # problem 3
                logging.info('Host %i has gathered and serviced a set' % self.id)
                pkts = [q.get(block=False) for q in self.packets_gather.itervalues()]

                if len(self.send_to) == 0:  # end for packet
                    for pkt in pkts:
                        self.finish_packet(env, pkt)
                else:
                    # figure out the oldest packet, use that packet to send forward
                    oldest_packet = min(pkts, key=lambda x: x.birth_tick)
                    oldest_packet.last_parent = self.id

                    comm_time = self.comm_dist(**self.comm_kwargs)

                    yield env.timeout(comm_time)
                    logging.info("Host %i finished communication after %f time" % (self.id, comm_time))

                    for host_id in self.send_to:
                        host = Host.get_hosts()[host_id]
                        host.packets.put(oldest_packet)
                        self.adjust_freq_after_send(oldest_packet, host)  # todo: assuming len(send_to) == 1 right now
                        logging.info('Host %i sent packet to host %i' % (self.id, host.id))

    def process_logging(self):
        env = get_env()

        while True:
            self.queue_size[env.now] = self.packets.qsize()
            self.freq_history.append(self.freq)
            yield env.timeout(1)

    def finish_packet(self, env, pkt):
		full_processing_time = env.now - pkt.birth_tick
		self.packet_latency.append(full_processing_time)
		logging.info('Host %i finished packet %i. time spent: %f' % (self.id, pkt.id, full_processing_time))

	# region control schemes
    def arrival_default_scheme(self):
        pass

    def arrival_basic(self):
        self.freq = np.interp(self.packets.qsize(), [0, 4], [self.min_freq, self.max_freq])

    def arrival_back_propagate(self):
        pass

    def after_send_default_scheme(self, pkt, dest):
        pass

    def after_send_back_propagate(self, pkt, dest):
        # first calculate the total number of packets at the destination
        total_packet_count = sum([q.qsize() for q in dest.packets_gather.values()])
        # get the packets_gather keys sorted by their queue size
        sorted_gather_queue_indicies =\
            [t[0] for t in sorted(dest.packets_gather.items(), key=lambda qu: qu[1].qsize())]
        rank = sorted_gather_queue_indicies.index(self.id)

        # scale the frequency by rank. Highest rank (most in queue) is slowest
        # lowest rank (least in queue) is fastest
        self.freq = np.interp(rank, [0, len(dest.packets_gather)], [self.min_freq, self.max_freq])

        logging.info('Host %i got back_propagate of %i/%i, setting freq to %f' % (self.id,
                                                                                  rank,
                                                                                  len(dest.packets_gather),
                                                                                  self.freq))
# endregion
