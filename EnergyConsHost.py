import logging
from simenv import get_env
import numpy as np
import itertools
from Queue import Queue
from Packet import Packet
from enum import Enum
from scipy.special import lambertw
import Host
import sys
import math
import random

def find_hosts(req_arr_rate, req_size, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers):
	# input: request arrival rate, request size
	# input: power consumption model (1 or 2)
	# request arrival rate (requests/s)
	# request size (cycles/request)
	
	# is e, epsilon
	
	min_servers = 0
	min_total_power = 1000000
	opt_servers = 0
	opt_freq = 0
	flag = 0	
	gamma = (alpha * d_0) / (math.exp(-alpha * d_0) - sys.float_info.epsilon)
	
	# determine min_servers to satisfy tail latency
	w = lambertw(-(sys.float_info.epsilon / math.exp(1)), -1).real

	if (1 / d_0) * math.log(1 / sys.float_info.epsilon) < alpha and alpha < ((1 / d_0) * (-w - 1)):
		w = lambertw(gamma * math.exp(sys.float_info.epsilon * gamma)).real
		min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (w - sys.float_info.epsilon * gamma)))
		flag = 1
	else:
		w = lambertw(gamma * math.exp(sys.float_info.epsilon * gamma), -1).real
		min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (w - sys.float_info.epsilon * gamma)))
		flag = 0
	
	min_servers = int(math.ceil(min_servers))
	
	if min_servers > num_of_servers:
		# min amount of servers needed exceeds available servers
		return -1 # no feasible solution
		
	# find optimal servers and optimal frequencies
	for i in range (min_servers, num_of_servers + 1):
		# # calculate optimal frequency
		# # is it req_arr_rate / i or req_arr_rate
		if pow_con_model == 1: 
			if b - (s_b / k_m) >= P_s:
					curr_freq = s_c
			else:		
				if flag:
					w = lambertw(gamma * math.exp(sys.float_info.epsilon * gamma)).real
					curr_freq = max(s_b, ((req_arr_rate / i)+ (1 / d_0) * (w - gamma*sys.float_info.epsilon) * req_size))
				else: 
					w = lambertw(gamma * math.exp(sys.float_info.epsilon * gamma), -1).real
					curr_freq = max(s_b, ((req_arr_rate / i) + (1 / d_0) * (w - gamma*sys.float_info.epsilon) * req_size))
		elif pow_con_model == 2:
			s_e = math.sqrt((b - P_s)*((k_m ^ 2) + (s_b ^ 2)))
			
			if s_e > s_c:
				curr_freq = s_c
			else:
				if flag:
					w = lambertw(gamma * math.exp(sys.float_info.epsilon * gamma)).real
					temp = (req_arr_rate / i) + ((1 / d_0) * (w - gamma*sys.float_info.epsilon) * req_size)
					
					if temp <= s_e and s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
				else:
					w = lambertw(gamma * math.exp(sys.float_info.epsilon * gamma), -1).real
					temp = (req_arr_rate / i) + ((1 / d_0) * (w - gamma*sys.float_info.epsilon) * req_size)
					
					if temp <= s_e and s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
		else:
			# error, model not found
			logging.error("Power consumption model not supported")
			return -1
	
		# calculate the power consumption of each server
		curr_total_power = ((1 / i) * req_arr_rate * req_size / curr_freq) * (b + (curr_freq - s_b / k_m)**pow_con_model) + (1 - ((1 / i) * req_arr_rate * req_size / curr_freq)) * P_s
		curr_total_power = i * curr_total_power
		
		# update the optimal servers if we found a new min_total_power
		if curr_total_power < min_total_power:
			min_total_power = curr_total_power
			opt_servers = i
			opt_freq = curr_freq
	
	print min_servers
	print min_total_power
	print opt_servers
	print opt_freq
	return opt_servers

class DistributionHost:
	def __init__(self, servers, arrival_distribution, arrival_kwargs):
		self.packets = Queue()
		self.servers = servers
		self.arrival_dist = arrival_distribution
		self.arrival_kwargs = arrival_kwargs
		
	def process_arrivals(self):
		env = get_env()
		
		while True:
			# create a new packet
			time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
			yield env.timeout(time_till_next_packet_arrival)
			pkt = Packet(env.now, 1)
			self.packets.put(pkt)
			logging.info('New packet received by main sever')
	
	def process_service(self):
		env = get_env()
		
		while True:
			# distribute packet to process host
			if self.packets.qsize() == 0:
					yield env.timeout(0.1)
					continue
			else:
				i = random.randint(0, Host.num_of_hosts - 1)
				#host = self.servers.get()
				p = self.packets.get()
				#host.packets.put(p)
				#self.servers.put(host)
				Host.hosts[i].packets.put(p)
				logging.info('Sending packet %i to host %i' %(p.id, Host.hosts[i].id))
				
				# host is asleep, wake it up
				if (Host.hosts[i].state == State.SLEEP):
					Host.hosts[i].wake_up_server()
				
				yield env.timeout(1)
				
# enumerate state values
class State(Enum):
	SLEEP = 0
	AWAKE = 1
	
# this assuming negligble forwarding times
class ProcessHost:
	def __init__(self, hostid, config, arrival_distribution, arrival_kwargs,
				 comp_time):
				 
				# class variables
				self.id = hostid
				self.arrival_dist = arrival_distribution
				self.arrival_kwargs = arrival_kwargs
				self.comp_time = comp_time
				self.state = State.SLEEP
				self.packets = Queue()

				# data collection
				self.energy_cons = list()
				self.packet_latency = list()
				self.queue_size = dict()
				self.freq_history = list()
	
	def __cmp__(self, other):
		return cmp(self.packets.qsize(), other.packets.qsize())
				
	def process_service(self):
		env = get_env()
		
		while True:
			# only process if the server is awake
			if (self.state == State.AWAKE): 
				# no packets in the queue
				if self.packets.qsize() == 0:
					if self.state == State.AWAKE:
						self.sleep_server()
						
					yield env.timeout(0.1)
					continue
				else:
					print "he"
					# determine computation time 
					pkt = self.packets.get()
					#yield env.timeout(self.comp_time)
					yield env.timeout(1)
					# determine power consumption
					
					# log the packet
					self.finish_packet(env, pkt)
			else:
				yield env.timeout(1)
					
	def finish_packet(self, env, pkt):
		full_processing_time = env.now - pkt.birth_tick
		self.packet_latency.append(full_processing_time)
		# add power consumption
		logging.info('Host %i finished packet %i. time spent: %f' % (self.id, pkt.id, full_processing_time))
	
	def wake_up_server(self):
		# calculate power consumption
		# this is static
		
		# calculate time to wake up
		time_to_wake_up = np.random.exponential(0.004)
		print time_to_wake_up
		yield env.timeout(time_to_wake_up)
		
		self.state = State.AWAKE
		logging.info('Host %i took %f time to wake up' %(self.id, 3.3))
		logging.info('Host %i consumed %f power to wake up' %(self.id, time_to_wake_up))
	
	def sleep_server(self):
		self.state = State.SLEEP
		logging.info('Host %i is now going to sleep' %(self.id))