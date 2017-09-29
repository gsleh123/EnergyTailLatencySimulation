from __future__ import division
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

# using ms 

def Energy_Runner(target_timestep):
	env = get_env()
	while env.now < target_timestep:
		yield env.timeout(1)
		#logging.info('Sim Time: %i' % env.now)

	#logging.info('Host Queue lengths after simulation:')
	#logging.debug('Distribution Host: %i' %(Host.main_host.packets.qsize()))
	for host in Host.get_hosts():
		queue_size = host.packets.qsize()
		if hasattr(host, 'packets_gather'):
			for q in host.packets_gather.values():
				queue_size += q.qsize()

		#logging.debug('Host %i: %i' % (host.id, queue_size))
	
	for host in Host.get_hosts():
		host.sleep_server(env)

def find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting, servers_to_use, freq_to_use):
	min_servers = 0
	min_total_power = 1000000
	opt_servers = 0
	opt_freq = 0
	flag = 0	
	servers = num_of_servers
	gamma = (alpha * d_0) / (math.exp(-(alpha * d_0)) - e)

	# determine min_servers to satisfy tail latency
	w = lambertw(-(e / math.exp(1)), -1).real
	
	if (1 / d_0) * math.log(1 / e) < alpha and alpha < ((1 / d_0) * (-w - 1)):
		w = lambertw(gamma * math.exp(e * gamma)).real	
		min_servers = (req_arr_rate / ((s_c / req_size) - ((1 / d_0) * (w - (e * gamma)))))
		flag = 1
	else:
		w = lambertw(gamma * math.exp(e * gamma), -1).real
		min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (w - e * gamma)))
		flag = 0
	
	min_servers = int(math.ceil(min_servers))
	
	if min_servers > num_of_servers:
		# min amount of servers needed exceeds available servers
		return -1, -1 # no feasible solution

	# depending on the problem type figure out the number of servers to use
	if problem_type == 1: 
		# optimal servers
		min_servers = min_servers
		num_of_servers = num_of_servers
	elif problem_type == 2: 
		# min servers 
		min_servers = min_servers
		num_of_servers = min_servers
	elif problem_type == 3:
		min_servers = num_of_servers
		num_of_servers = num_of_servers
		
	# find optimal servers and optimal frequencies
	for i in range (min_servers, num_of_servers + 1):
		# calculate optimal frequency
		if pow_con_model == 1: 
			if b - (s_b / k_m) >= P_s:
					curr_freq = s_c
					#print "do"
			else:		
				if flag:
					w = lambertw(gamma * math.exp(e * gamma)).real
					curr_freq = max(s_b, (((req_arr_rate / i)+ (1 / d_0) * (w - gamma*e)) * req_size))
				else: 
					w = lambertw(gamma * math.exp(e * gamma), -1).real
					curr_freq = max(s_b, (((req_arr_rate / i)+ (1 / d_0) * (w - gamma*e)) * req_size))
		elif pow_con_model == 2:
			s_e = math.sqrt(((b - P_s)*(k_m ** 2)) + (s_b ** 2))
			
			if s_e > s_c:
				curr_freq = s_c
			else:
				if flag:
					w = lambertw(gamma * math.exp(e * gamma)).real
					temp = ((req_arr_rate / i) + (1 / d_0) * (w - gamma*e)) * req_size
	
					if temp <= s_e and s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
				else:
					w = lambertw(gamma * math.exp(e * gamma), -1).real
					temp = ((req_arr_rate / i) + ((1 / d_0) * (w - gamma*e))) * req_size
					
					if temp <= s_e and s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
	
		# calculate the power consumption of each server
		curr_total_power = (((1 / i) * req_arr_rate * req_size / curr_freq) * (b + ((curr_freq - s_b) / k_m)**pow_con_model)) + ((1 - ((1 / i) * req_arr_rate * req_size / curr_freq)) * P_s)
		curr_total_power = i * curr_total_power
	
		# update the optimal servers if we found a new min_total_power
		if curr_total_power < min_total_power:
			min_total_power = curr_total_power
			opt_servers = i
			opt_freq = curr_freq
	
	if freq_setting == 2:
		# we want the max freq which is S_c
		opt_freq = s_c 

	if problem_type == 4:
		opt_servers = servers_to_use
		opt_freq = freq_to_use

	Host.csv_temp_list.append(req_arr_rate)
	Host.csv_temp_list.append(opt_servers)
	Host.csv_temp_list.append(opt_freq / 10**9)
	
	#logging.info("Arrival rate: %i" %(req_arr_rate))
	#logging.info("Minimum Servers: %i" %(min_servers))
	#logging.info("Optimal Servers: %i" %(opt_servers))
	#logging.info("Optimal Frequency: %f" %(opt_freq))

	return opt_servers, opt_freq

# enumerate state values
class State(Enum):
	SLEEP = 0
	BOOTING = 1
	AWAKE = 2
	
class DistributionHost:
	def __init__(self, arrival_distribution, arrival_kwargs, arrival_rate, alphaThresh, betaThresh):
		self.packets = Queue()
		self.arrival_dist = arrival_distribution
		self.arrival_kwargs = arrival_kwargs
		self.arrival_rate = arrival_rate 
		self.alphaThresh = alphaThresh
		self.betaThresh = betaThresh
		
		self.arrival_times = list()
		self.count = 0

	def process_arrivals_synthetic(self):
		env = get_env()
		arrival_rate = self.arrival_rate
		state = 1
		constOffset = 1000 / arrival_rate / 1000;
		alphaThresh = self.alphaThresh
		betaThresh = self.betaThresh

		while True:
			if state == 0:
				# generate traffic really quickly 
				
				beta = np.random.uniform(0, 1)
				
				if beta <= betaThresh:
					state = 1
				else:
					state = 0

				yield env.timeout(10)
			else:
				# generate traffic a bit slower
				time_till_next_packet_arrival = np.random.exponential(arrival_rate)
				alpha = np.random.uniform(0, 1)
					
				if alpha <= alphaThresh:
					state = 1
				else:
					state = 0
		
				yield env.timeout(time_till_next_packet_arrival)

				self.arrival_times.append(time_till_next_packet_arrival)
				self.create_packet(env)

	def process_arrivals_real(self, real_traffic):
		env = get_env()

		while True:
			time_till_next_packet_arrival = real_traffic[self.count]
			self.count = self.count + 1

			if self.count == len(real_traffic):
				self.count = 0

			yield env.timeout(time_till_next_packet_arrival)
			self.arrival_times.append(time_till_next_packet_arrival)
	
			self.create_packet(env)

	def create_packet(self, env):
		pkt = Packet(env.now)

		# send packet away
		i = random.randint(0, Host.num_of_hosts - 1)
		Host.hosts[i].packets.put(pkt)
		
		# wake up server if we found it to be sleeping
		if Host.hosts[i].state == State.SLEEP:
 			Host.hosts[i].wake_up_server(env)
		
class ProcessHost:
	def __init__(self, hostid, config, comp_time, arrival_dist, arrival_kwargs, wake_up_dist, wake_up_kwargs, power_setup):
				 
				# class variables
				self.id = hostid
				self.comp_time = comp_time
				self.arrival_dist = arrival_dist
				self.arrival_kwargs = arrival_kwargs
				self.wake_up_dist = wake_up_dist
				self.wake_up_kwargs = wake_up_kwargs
				self.power_setup = power_setup
				self.state = State.SLEEP
				self.packets = Queue()
				self.start_timer = 0
				self.end_timer = 0
				
				# data collection
				self.computing_times = list()
				self.wake_up_times = list()
				self.sleep_times = list()
				self.packet_latency = list()
				self.queue_size = dict()
				self.freq_history = list()
	
	def __cmp__(self, other):
		# I don't think we use this anymore
		return cmp(self.packets.qsize(), other.packets.qsize())
				
	def process_service(self):
		env = get_env()
		
		while True:
			if (self.state == State.AWAKE): 
				# only process if the server is awake
				if self.packets.qsize() == 0:
					#empty queue
					
					# this lets the simulator check if there are really no more packets in the queue
					#yield env.timeout(1)
					
					if self.packets.qsize() == 0:
						self.sleep_server(env)
						
					continue
				else:
					# determine computation time
					comp_time = np.random.exponential(self.comp_time)
					pkt = self.packets.get()
					
					yield env.timeout(comp_time)
					
					# log the packet
					self.finish_packet(env, pkt)
			elif self.state == State.BOOTING:
				# we are booting, so we need to figure out for how long
				
				time_to_wake_up = self.wake_up_dist(**self.wake_up_kwargs)
			
				self.end_timer = env.now
				diff = self.end_timer - self.start_timer
				self.sleep_times.append(diff)
			
				self.wake_up_times.append(time_to_wake_up)
				yield env.timeout(time_to_wake_up)

				self.finish_booting_server(env, time_to_wake_up)
			else:
				# do nothing, we are already asleep
				time_to_wait = self.arrival_dist(**self.arrival_kwargs) / 2
				yield env.timeout(time_to_wait)
					
	def finish_packet(self, env, pkt):
		full_processing_time = env.now - pkt.birth_tick
		self.packet_latency.append(full_processing_time)

		#logging.info('Host %i finished a packet. time spent: %f' % (self.id, full_processing_time))
	
	def wake_up_server(self, env):
		self.state = State.BOOTING
				
	def finish_booting_server(self, env, time_to_wake_up):
		self.start_timer = env.now
		self.state = State.AWAKE
		
	def sleep_server(self, env):
		self.end_timer = env.now
		diff = self.end_timer - self.start_timer
		self.start_timer = env.now
		self.computing_times.append(diff)
		self.state = State.SLEEP
