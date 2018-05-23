import logging
from simenv import get_env
import numpy as np
from collections import namedtuple
import itertools
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
	num_of_hosts = 0
	report_type = config['mpip_report_type']
	csv_temp_list = list()

	# set up the distribution host
	arrival_distribution = config['Energy']['arrival_distribution']
	arrival_kwargs = config['Energy']['arrival_kwargs']
	arrival_rate = config['arrival_rate']
	alphaThresh = config['Energy']['alphaThresh']
	betaThresh = config['Energy']['betaThresh']
	routing_option = config['Energy']['routing_option']

	# retrieve all the settings
	real_data = config['Energy']['real_data']
	wake_up_dist = config['Energy']['wake_up_distribution']
	wake_up_kwargs = config['Energy']['wake_up_kwargs']
	req_arr_rate = 1000 / np.mean(real_data) if len(real_data) != 0 else config['arrival_rate']
	req_size = config['req_size']
	d_0 = config['Energy']['d_0']
	P_s = config['Energy']['P_s']
	alpha = config['Energy']['alpha']
	num_of_servers = config['Energy']['num_of_servers']
	e = config['Energy']['e']
	s_b = config['Energy']['s_b']
	max_freq = s_c = config['Energy']['s_c']
	pow_con_model = config['Energy']['pow_con_model']
	k_m = config['Energy']['k_m']
	b = config['Energy']['b']
	problem_type = config['Energy']['problem_type']
	freq_setting = config['Energy']['freq_setting']
	active_servers = config['Energy']['active_servers']
        servers_to_use = config['Energy']['servers_to_use']
	freq_to_use = config['Energy']['freq_to_use']
	dvfs_option = config['Energy']['dvfs_option']
	
        main_host = ech.DistributionHost(arrival_distribution, arrival_kwargs, arrival_rate, alphaThresh, betaThresh, routing_option, active_servers)

	# determine optimal number of servers and optimal frequency
	dimension_depth = 2
	[num_of_hosts, freq] = ech.find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting, servers_to_use, freq_to_use)
	
	# error
	if (num_of_hosts == -1):
		return 0
				
	for i in range(num_of_hosts):
		# instantiate a new host
		host = ech.ProcessHost(i, config, req_size, freq, max_freq, arrival_distribution, arrival_kwargs, arrival_rate, wake_up_dist, wake_up_kwargs, dvfs_option)
		hosts.append(host)

	env = get_env()
	
	if (len(real_data) != 0):
		#env.process(main_host.refresh_system(real_data))
		env.process(main_host.process_arrivals_real(real_data))
	else:
		env.process(main_host.process_arrivals_theoretical())
		#env.process(main_host.process_arrivals_synthetic_mode())
		#env.process(main_host.process_arrivals_synthetic())
	
	for i in np.random.permutation(num_of_hosts):
		env.process(hosts[i].process_service())

	target_timestep = config['timesteps']
		
	return get_env().process(ech.Energy_Runner(target_timestep))

def get_hosts():
	global hosts
	return hosts
