import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
from Packet import Packet
import Host
import sys

def find_hosts(req_arr_rate, req_size):
	# input: request arrival rate and request size
	# request arrival rate (requests/s)
	# request size (cycles/request)
	
	min_servers = 0; 
	min_total_power = 1000000;
	opt_servers = 0; 

	# determine min_servers to satisy tail latency
	if d_0 * ln(1/e)... :
		min_servers = 
	else:
		min_servers = 
		
	if (min_servers > num_of_servers):
		# min amount of servers needed exceeds available servers
		break; # no feasible solution
	# determine min_servers to satisy tail latency

	# find optimal servers and optimal frequencies
	for :
		# calculate optimal frequency
		# calculate the power consumption of each
		# something with min_total_power
		
		if something:
			
# we should another host that is the root node
# added a state variable: there should be three states sleep, awake, busy
# added a list for energy consumption in data collection
# need to add wake time from sleep to 
class LeafNode:
	def __init__(self, hostid, config, arrival_distribution, arrival_kwargs, comm_distribution, comm_kwargs,
                 comp_time, send_to, should_generate, control_scheme, state):
				 
				# class variables
				self.id = hostid
				self.arrival_dist = arrival_distribution
				self.arrival_kwargs = arrival_kwargs
				self.comm_dist = comm_distribution
				self.comm_kwargs = comm_kwargs
				self.comp_time = comp_time
				self.send_to = send_to
				self.should_generate = should_generate
				self.problem_type = config['Abstract']['problem_type']
				self.state = awake
				self.packets = Queue()

				# data collection
				self.energy_cons = list()
				self.packet_latency = list()
				self.queue_size = dict()
				self.freq_history = list()
				
	def process_arrivals(self):
        env = get_env()

        while True:
            if self.should_generate:
                time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
                yield env.timeout(time_till_next_packet_arrival)
                pkt = Packet(env.now, self.id)
                self.packets.put(pkt)
				# if server is asleep, wake up server
                logging.info('Host %i generated a packet %i after %f time' % (self.id, pkt.id, time_till_next_packet_arrival))
            else:
                yield env.timeout(0.1)
				
	def process_service(self):
        env = get_env()
		# if server is asleep don't process anything
        while True:

            if self.problem_type != 3:
                if self.packets.qsize() == 0:
                    yield env.timeout(0.1)
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
					
	def finish_packet(self, env, pkt):
        full_processing_time = env.now - pkt.birth_tick
        self.packet_latency.append(full_processing_time)
        logging.info('Host %i finished packet %i. time spent: %f' % (self.id, pkt.id, full_processing_time))
	
	def wake_up_server(self):
		# calculate power consumption
		# calculate time to wake up
		self.state = awake
		logging.info('Host %i took %f time to wake up' %(self.id, ))
		logging.info('Host %i consumed %f power to wake up' %(self.id, ))
	
	def sleep_server(self):
		self.state = sleep