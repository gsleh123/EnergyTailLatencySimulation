import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
from Packet import Packet
from enum import Enum
import Host
import sys
import math

def find_hosts(req_arr_rate, req_size, d_0, e, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers):
	# input: request arrival rate, request size
	# input: power consumption model (1 or 2)
	# request arrival rate (requests/s)
	# request size (cycles/request)
	
	# what is w? 
	# what is gamma 
	
	min_servers = 0
	min_total_power = 1000000
	opt_servers = 0
	opt_freq = 0
	flag = 0
	
	# determine min_servers to satisfy tail latency
	if ((1 / d_0) * ln(1 / e) < alpha) && (alpha < (1 / d_0) * ...):
		min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (w_0) * (...)))
		flag = 1
	else:
		min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (...) * (...)))
		flag = 0
		
	if min_servers > num_of_servers:
		# min amount of servers needed exceeds available servers
		break; # no feasible solution
	# determine min_servers to satisy tail latency

	# find optimal servers and optimal frequencies
	for i in range (min_servers, num_of_servers + 1):
		# calculate optimal frequency
		# is it req_arr_rate / i or req_arr_rate
		if pow_con_model == 1: 
			if b - (s_b / k_m) >= P_s:
					curr_freq = s_c
			else:		
				if flag:
					curr_freq = max(s_b, (req_arr_rate + (1 / d_0)*(...))
				else: 
					curr_freq = max(s_b, (req_arr_rate + (1 / d_0)*(...))
		elif pow_con_model == 2:
			s_e = math.sqrt((b - P_s)*((k_m ^ 2) + (s_b ^ 2)))
			
			if s_e > s_c:
				curr_freq = s_c
			else:
				if flag:
					temp = req_arr_rate + *(1 / d_0) * (...) * req_size)
					
					if temp <= s_e && s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
				else
					temp = req_arr_rate + *(1 / d_0) * (...) * req_size)
					
					if temp <= s_e && s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
		else:
			# error, model not found
			logging.error("Power consumption model not supported")
			return -1
			
		# calculate the power consumption of each server
		
		# update the optimal servers if we found a new min_total_power
		if curr_total_power < min_total_power:
			min_total_power = curr_total_power
			opt_servers = i
			opt_freq = curr_freq

# enumerate state values
class State(Enum):
	SLEEP = 0
	AWAKE = 1
	
# this assuming negligble forwarding times
class Server:
	def __init__(self, hostid, config, arrival_distribution, arrival_kwargs,
                 comp_time):
				 
				# class variables
				self.id = hostid
				self.arrival_dist = arrival_distribution
				self.arrival_kwargs = arrival_kwargs
				self.comp_time = comp_time
				self.state = State.AWAKE
				self.packets = Queue()

				# data collection
				self.energy_cons = list()
				self.packet_latency = list()
				self.queue_size = dict()
				self.freq_history = list()
				
	def process_arrivals(self):
        env = get_env()

        while True:
			# need to fix the fix the distribution
			time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
			yield env.timeout(time_till_next_packet_arrival)
			pkt = Packet(env.now, self.id)
			self.packets.put(pkt)
			logging.info('Host %i generated a packet %i after %f time' % (self.id, pkt.id, time_till_next_packet_arrival))
			
			# server is asleep, wake it up
			if (self.state == State.SLEEP):
				self.wake_up_server()
				
	def process_service(self):
        env = get_env()
		
        while True:
			# only process if the server is awake
			if (self.state == state.AWAKE): 
				# no packets in the queue
				if self.packets.qsize() == 0:
                    yield env.timeout(0.1)
                    continue
				
				# determine computation time 
				
				# determine power consumption
				
				# log the packet
				self.finish_packet(env, pkt)
				
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
		# add power consumption
        logging.info('Host %i finished packet %i. time spent: %f' % (self.id, pkt.id, full_processing_time))
	
	def wake_up_server(self):
		# calculate power consumption
		
		# calculate time to wake up
		
		self.state = State.AWAKE
		logging.info('Host %i took %f time to wake up' %(self.id, ))
		logging.info('Host %i consumed %f power to wake up' %(self.id, ))
	
	def sleep_server(self):
		self.state = State.SLEEP
		logging.info('Host %i is now going to sleep', %(self.id))