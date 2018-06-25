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

    for host in Host.get_hosts():
        queue_size = host.packets.qsize()
	if hasattr(host, 'packets_gather'):
            for q in host.packets_gather.values():
	        queue_size += q.qsize()

    for host in Host.get_hosts():
        host.end_sim(env)

def find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting, servers_to_use, freq_to_use):
    min_servers = 0
    min_total_power = float('inf')
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

    return opt_servers, opt_freq

# enumerate state values
class State(Enum):
    SLEEP = 0
    BOOTING = 1
    AWAKE = 2
	
class DistributionHost:
    def __init__(self, arrival_distribution, arrival_kwargs, arrival_rate, alphaThresh, betaThresh, routing_option, active_servers, timescale, e):
	self.packets = Queue()
	self.arrival_dist = arrival_distribution
	self.arrival_kwargs = arrival_kwargs
	self.arrival_rate = arrival_rate 
	self.alphaThresh = alphaThresh
	self.betaThresh = betaThresh
	self.num_packets = 0	
	self.arrival_times = list()
	self.count = 0
	self.routing_option = routing_option
        self.active_servers = active_servers
        self.min_servers = active_servers
        self.packetCount = 0
        self.packetFlag = 0

	# only used for ipp traffic
	self.state = 1
	self.switch = False

        self.e = e

    def process_arrivals_theoretical(self):
	env = get_env()
		
	while True:
	    time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
	    yield env.timeout(time_till_next_packet_arrival)
	    self.arrival_times.append(time_till_next_packet_arrival)
 	    self.create_packet(env)
	    self.num_packets = self.num_packets + 1

    def process_arrivals_ipp(self):
        env = get_env()
	arrival_rate = self.arrival_rate
	state = self.state
	constOffset = timescale / arrival_rate / timescale;
	alphaThresh = self.alphaThresh
	betaThresh = self.betaThresh
	k = alphaThresh / betaThresh
	time_to_switch = 0

	while True:
	    state = self.state
	    switch = self.switch

	    if state == 0:
		# generate traffic really quickly 
	        time_to_wait = np.random.exponential(timescale / arrival_rate * (1 / (1 + alphaThresh/betaThresh)))

		yield env.timeout(time_to_wait)
	    else:
		time_till_next_packet_arrival = np.random.exponential(timescale/arrival_rate * (1 / (1  + alphaThresh/betaThresh)))
		yield env.timeout(time_till_next_packet_arrival)
				
		self.arrival_times.append(time_till_next_packet_arrival)
		self.create_packet(env)
		self.num_packets = self.num_packets + 1
		
    def process_arrivals_ipp_mode(self):
	env = get_env()

	while True:
	    state = self.state
			
	    if state == 0:
		time_to_switch = np.random.exponential(1 / self.betaThresh)
	    else:
		time_to_switch = np.random.exponential(1 / self.alphaThresh)

	    yield env.timeout(time_to_switch)
			
	    if (self.state == 1):
		self.state = 0
	    else:
	        self.state = 1

    def process_arrivals_real(self, real_traffic):
	env = get_env()

	while True:
	    time_till_next_packet_arrival = real_traffic[self.count]
	    self.count = self.count + 1

	    if self.count == len(real_traffic):
		self.count = 0

	    yield env.timeout(time_till_next_packet_arrival)
	    self.arrival_times.append(time_till_next_packet_arrival)
	    self.num_packets = self.num_packets + 1	
	    self.create_packet(env)

    def create_packet(self, env):
	# determine which host to send the packet to
	i = 0
        #print(self.active_servers)
	if self.routing_option == 'min_queue_length':
	    min_queue_len = float("inf")
            for x in range(self.active_servers):
                queue_len = Host.hosts[x].packets.qsize()
                if queue_len < min_queue_len:
                    i = x
                    min_queue_len = queue_len
	else:
	    i = random.randint(0, self.active_servers - 1)

	#create packet
	pkt = Packet(env.now, Host.hosts[i].packets.qsize())

	#place packet in the queue
	Host.hosts[i].packets.put(pkt)
    
        constInt = 15

	# wake up server if we found it to be sleeping
	if Host.hosts[i].state == State.SLEEP:
 	    Host.hosts[i].wake_up_server(env)

        if self.packetFlag:
            self.packetCount = self.packetCount + 1

            if self.packetCount >= int(self.arrival_rate * constInt):
                self.packetFlag = 0
        
        total_latency = list()
        for x in range(self.active_servers):
            packet_latency_len = min(len(Host.hosts[i].packet_latency), int((self.arrival_rate * constInt / self.active_servers) + 1))
            total_latency = total_latency + Host.hosts[i].packet_latency[-packet_latency_len:]
        
        if len(total_latency) >= int(self.arrival_rate * constInt)  and not self.packetFlag:
            temp = 0
            d_0 = 0.5 * self.timescale

            for latency in total_latency:
                if latency > d_0:
                    temp+=1

            if len(total_latency) > 0:
                prob_lifetimes = temp / len(total_latency)
            else:
                prob_lifetimes = 0

            if prob_lifetimes > self.e:
                max_servers = len(Host.hosts)
                self.active_servers = min(self.active_servers + 1, max_servers)
                self.packetFlag = 1
                self.packetCount = 0
            else:
                min_servers = self.min_servers
                self.active_servers = max(self.active_servers - 1, min_servers)
		
class ProcessHost:
    def __init__(self, hostid, config, req_size, freq, max_freq, arrival_dist, arrival_kwargs, arrival_rate, wake_up_dist, wake_up_kwargs, dvfs_option):
        # class variables
        self.id = hostid
        self.timescale = config['timescale']
        self.comp_time = (self.timescale * req_size) / freq
	self.req_size = req_size
        self.fixed_freq = self.freq = freq
	self.max_freq = max_freq
	self.arrival_dist = arrival_dist
	self.arrival_kwargs = arrival_kwargs
	self.arrival_rate = arrival_rate
	self.wake_up_dist = wake_up_dist
	self.wake_up_kwargs = wake_up_kwargs
	self.state = State.SLEEP
	self.packets = Queue()
	self.start_timer = 0
	self.end_timer = 0
	self.dvfs_option = dvfs_option

	# data collection
        self.computing_times = list()
        self.wake_up_times = list()
	self.sleep_times = list()
	self.packet_latency = list()
	self.packet_comp_time = list()
        self.packet_freq_history = list()
        self.queue_size = dict()
	
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
		    self.sleep_server(env)				
		    continue
		else:
		    # determine computation time
		    comp_time = np.random.exponential(self.comp_time)
		    pkt = self.packets.get()
		    yield env.timeout(comp_time)

		    self.finish_packet(env, pkt, comp_time, self.freq)

		    freq = self.fixed_freq

		    if self.dvfs_option == 'rubik':
                        if self.packets.qsize() != 0:
			    for i in range(self.packets.qsize()):
                                time_spent_in_sys = (env.now - pkt.birth_tick) / self.timescale
                                temp_freq = (self.fixed_freq / 2) / (0.5 - time_spent_in_sys)
							
				if temp_freq > freq:
				    freq = temp_freq

				freq = min(freq, self.max_freq)

                            self.comp_time = (self.timescale * self.req_size) / (freq)
			    self.freq = freq
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
		time_to_wait = self.timescale / self.arrival_rate / 10
		yield env.timeout(time_to_wait)
					
    def finish_packet(self, env, pkt, comp_time, freq):
	full_processing_time = env.now - pkt.birth_tick
	self.packet_latency.append(full_processing_time)
	self.packet_comp_time.append(comp_time)
	self.packet_freq_history.append(freq)
	
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

    def end_sim(self, env):
        if self.state == State.SLEEP:
            self.end_timer = env.now
            diff = self.end_timer - self.start_timer
            self.start_timer = env.now
            self.sleep_times.append(diff)
            self.state = State.SLEEP
        else:
            self.sleep_server(env)

