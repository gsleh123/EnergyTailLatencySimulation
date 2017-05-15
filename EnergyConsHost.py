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

# using nanoseconds 

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

def find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers):
	# input: request arrival rate, request size
	# input: power consumption model (1 or 2)
	# request arrival rate (requests/s)
	# request size (cycles/request)
		
	min_servers = 0
	min_total_power = 1000000
	opt_servers = 0
	opt_freq = 0
	flag = 0	
	gamma = (alpha * d_0) / (math.exp(-(alpha * d_0)) - e)

	# determine min_servers to satisfy tail latency
	w = lambertw(-(e / math.exp(1)), -1).real
	#print (1 / d_0) * math.log(1 / e) 
	#print w
	#print ((1 / d_0) * (-w - 1))
	if (1 / d_0) * math.log(1 / e) < alpha and alpha < ((1 / d_0) * (-w - 1)):
		w = lambertw(gamma * math.exp(e * gamma)).real		
		min_servers = (req_arr_rate / ((s_c / req_size) - ((1 / d_0) * (w - (e * gamma)))))
		flag = 1
	else:
		w = lambertw(gamma * math.exp(e * gamma), -1).real
		min_servers = (req_arr_rate / ((s_c / req_size) - (1 / d_0) * (w - e * gamma)))
		flag = 0
	
	#print min_servers
	min_servers = int(math.ceil(min_servers))
	
	if min_servers > num_of_servers:
		# min amount of servers needed exceeds available servers
		return -1 # no feasible solution

	# find optimal servers and optimal frequencies
	for i in range (min_servers, num_of_servers + 1):
		# calculate optimal frequency
		if pow_con_model == 1: 
			if b - (s_b / k_m) >= P_s:
					curr_freq = s_c
					print "do"
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
					temp = (req_arr_rate / i) + ((1 / d_0) * (w - gamma*e) * req_size)
					
					if temp <= s_e and s_e <= s_c:
						curr_freq = s_e
					else:
						curr_freq = temp
				else:
					w = lambertw(gamma * math.exp(e * gamma), -1).real
					temp = (req_arr_rate / i) + ((1 / d_0) * (w - gamma*e) * req_size)
					
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
	
	#print "min_servers "
	#print min_servers
	#print "min_total_power "
	#print min_total_power
	#print "opt_servers "
	#print opt_servers
	#print "opt_freq "
	#print opt_freq
	logging.info("Minimum Servers: %i" %(min_servers))
	logging.info("Optimal Servers: %i" %(opt_servers))
	logging.info("Optimal Frequency: %f" %(opt_freq))
		
	return opt_servers, opt_freq

# enumerate state values
class State(Enum):
	SLEEP = 0
	BOOTING = 1
	AWAKE = 2
	
class DistributionHost:
	def __init__(self, arrival_distribution, arrival_kwargs):
		self.packets = Queue()
		self.arrival_dist = arrival_distribution
		self.arrival_kwargs = arrival_kwargs
		
	def process_arrivals(self):
		env = get_env()
		
		while True:
			# create a new packet
			#time_till_next_packet_arrival = self.arrival_dist(0.1)
			time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
			yield env.timeout(time_till_next_packet_arrival)
			
			pkt = Packet(env.now)
			self.packets.put(pkt)
			#logging.info('New packet received by main sever')
	
	def process_service(self):
		env = get_env()
		
		while True:
			# distribute packet to process host
			if self.packets.qsize() == 0:
					yield env.timeout(0.1)
					continue
			else:
				i = random.randint(0, Host.num_of_hosts - 1)
				p = self.packets.get()
				Host.hosts[i].packets.put(p)
				#logging.info('Sending packet %i to host %i' %(p.id, Host.hosts[i].id))
				#time_to_send = self.arrival_dist(**self.arrival_kwargs)
				time_to_send = 0.1
				#print "sending packet"

				yield env.timeout(time_to_send)
				
# this assuming negligble forwarding times
class ProcessHost:
	def __init__(self, hostid, config, comp_time, wake_up_dist, wake_up_kwargs, power_setup):
				 
				# class variables
				self.id = hostid
				self.comp_time = comp_time
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
		return cmp(self.packets.qsize(), other.packets.qsize())
				
	def process_service(self):
		env = get_env()
		
		while True:
			# only process if the server is awake
			if (self.state == State.AWAKE): 
				# no packets in the queue
				if self.packets.qsize() == 0:
					# this lets the simulator check if there are really no more packets in the queue
					#yield env.timeout(1)
					
					if self.packets.qsize() == 0:
						self.sleep_server(env)
						
					continue
				else:
					# determine computation time
					# should be req size / freq
					#comp_time = np.random.exponential(0.000333)
					comp_time = np.random.exponential(self.comp_time)
					pkt = self.packets.get()
					yield env.timeout(comp_time)
					
					# log the packet
					self.finish_packet(env, pkt)
			elif (self.state == State.SLEEP and self.packets.qsize() != 0):
				time_to_wake_up = self.wake_up_dist(**self.wake_up_kwargs)
				
				# calculate sleep times
				self.end_timer = env.now
				diff = self.end_timer - self.start_timer
				self.sleep_times.append(diff)
				
				# append wake up times to list
				self.wake_up_times.append(time_to_wake_up)
				self.state = State.BOOTING
				#logging.info('Host %i is booting up' %(self.id))
				
				yield env.timeout(time_to_wake_up)
				
				self.finish_booting_server(env, time_to_wake_up)
			else:
				yield env.timeout(0.1)
					
	def finish_packet(self, env, pkt):
		full_processing_time = env.now - pkt.birth_tick
		self.packet_latency.append(full_processing_time)
		#logging.info('Host %i finished a packet. time spent: %f' % (self.id, full_processing_time))
	
	def finish_booting_server(self, env, time_to_wake_up):
		self.start_timer = env.now
		#logging.info('Host %i took %f time to wake up' %(self.id, time_to_wake_up))
		self.state = State.AWAKE
		
	def sleep_server(self, env):
		self.end_timer = env.now
		diff = self.end_timer - self.start_timer
		self.start_timer = env.now
		self.computing_times.append(diff)
		self.state = State.SLEEP
		#logging.info('Host %i is now going to sleep' %(self.id))