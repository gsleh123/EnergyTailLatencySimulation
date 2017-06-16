import logging
from simenv import get_env
import numpy as np
from collections import namedtuple
import itertools
import MILCHost
import AbstractHost
import EnergyConsHost as ech
import sys
from Queue import Queue

hosts = []

lognormal_param = namedtuple('lognormal_param', 'mean sigma')

def init_hosts(config):
	global hosts
	global num_of_hosts
	global main_host
	global csv_temp_list
	
	hosts = []
	num_of_hosts = config['host_count']
	report_type = config['mpip_report_type']
	csv_temp_list = list()

	# set up the distribution host
	arrival_distribution = config['Abstract']['arrival_distribution']
	arrival_kwargs = config['Abstract']['arrival_kwargs']
	arrival_rate = config['arrival_rate']
	main_host = ech.DistributionHost(arrival_distribution, arrival_kwargs, arrival_rate)

	# retrieve all the settings
	wake_up_dist = config['Abstract']['wake_up_distribution']
	wake_up_kwargs = config['Abstract']['wake_up_kwargs']
	req_arr_rate = config['arrival_rate']
	req_size = config['req_size']
	d_0 = config['Abstract']['d_0']
	P_s = config['Abstract']['P_s']
	alpha = config['Abstract']['alpha']
	num_of_servers = config['Abstract']['num_of_servers']
	e = config['Abstract']['e']
	s_b = config['Abstract']['s_b']
	s_c = config['Abstract']['s_c']
	pow_con_model = config['Abstract']['pow_con_model']
	k_m = config['Abstract']['k_m']
	b = config['Abstract']['b']
	problem_type = config['Abstract']['problem_type']
	freq_setting = config['Abstract']['freq_setting']

	# determine optimal number of servers and optimal frequency
	dimension_depth = 2
	[num_of_hosts, freq] = ech.find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting)
	comp_time = (1000 * req_size) / (freq)
	
	# error
	if (num_of_hosts == -1):
		return 0
		
	for i in range(num_of_hosts):
		# instantiate a new host
		host = ech.ProcessHost(i, config, comp_time, arrival_distribution, arrival_kwargs, wake_up_dist, wake_up_kwargs, P_s)
		hosts.append(host)

	env = get_env()
	env.process(main_host.process_arrivals())
	
	for i in np.random.permutation(num_of_hosts):
		env.process(hosts[i].process_service())

	target_timestep = config['timesteps']
		
	return get_env().process(ech.Energy_Runner(target_timestep))

def get_hosts():
	global hosts
	return hosts
