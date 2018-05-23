import random
import logging
import numpy as np
import time
import scipy.stats
import ast
import Host
from simenv import get_env
import Vis_Energy
import sys

def run(parser):	
	config = create_config_dict(parser)
	
	config['timescalar'] = 1/1.
	report_type = config['mpip_report_type']

	env = get_env()
	proc = Host.init_hosts(config)

	Vis_Energy.setup()
		
	time.sleep(1)

	#logging.info('Simulation Started')

	env.run(proc)

	#logging.info('Simulation Complete')

	total_computing_time = 0
	total_wake_up_time = 0
	total_sleep_time = 0
	for host in Host.hosts:
		total_computing_time += sum(host.computing_times)
		total_wake_up_time += sum(host.wake_up_times)
		total_sleep_time += sum(host.sleep_times)
	
	total_time = total_computing_time + total_wake_up_time + total_sleep_time
	comp_ratio = total_computing_time / total_time
	wake_up_ratio = total_wake_up_time / total_time
	sleep_ratio = total_sleep_time / total_time
	Host.csv_temp_list.append(comp_ratio)
	Host.csv_temp_list.append(wake_up_ratio)
	Host.csv_temp_list.append(sleep_ratio)
	
	Vis_Energy.show_graphs(config)
	
def create_config_dict(parser):
	# we use a dict to pass the options around
	options = dict()

	# if no seed present, use python's inbuilt generator
	if parser.has_option('CC_Config', 'seed'):
		seed = int(parser.get('CC_Config', 'seed'))
		random.seed(seed)
		np.random.seed(seed)

	req_size = int(parser.get('CC_Config', 'req_size'))
	options['req_size'] = req_size

	timesteps = 100
	if parser.has_option('CC_Config', 'timesteps'):
		timesteps = int(parser.get('CC_Config', 'timesteps'))
	options['timesteps'] = timesteps

	mpip_report_type = ''
	if parser.has_option('CC_Config', 'mpip_report_type'):
		mpip_report_type = parser.get('CC_Config', 'mpip_report_type')
	options['mpip_report_type'] = mpip_report_type

	options['Energy'] = dict()
	options['Energy']['problem_type'] = int(parser.get('Energy', 'problem_type'))
	options['Energy']['freq_setting'] = int(parser.get('Energy', 'freq_setting'))

        options['Energy']['sim_mode'] = str(parser.get('Energy', 'sim_mode'));
	options['Energy']['d_0'] = float(parser.get('Energy', 'd_0'));
	options['Energy']['P_s'] = int(parser.get('Energy', 'P_s'));
	options['Energy']['alpha'] = int(parser.get('Energy', 'alpha'));
	options['Energy']['num_of_servers'] = int(parser.get('Energy', 'num_of_servers'));
	options['Energy']['e'] = float(parser.get('Energy', 'e'));
	options['Energy']['s_b'] = float(parser.get('Energy', 's_b')) * 10**9;
	options['Energy']['s_c'] = float(parser.get('Energy', 's_c')) * 10**9;
	options['Energy']['pow_con_model'] = int(parser.get('Energy', 'pow_con_model'));
	options['Energy']['k_m'] = float(parser.get('Energy', 'k_m')) * 10**9;
	options['Energy']['b'] = int(parser.get('Energy', 'b'));
	options['Energy']['alphaThresh'] = float(parser.get('Energy', 'alphaThresh'));
	options['Energy']['betaThresh'] = float(parser.get('Energy', 'betaThresh'));
	options['Energy']['active_servers'] = int(parser.get('Energy', 'active_servers'));
        options['Energy']['servers_to_use'] = int(parser.get('Energy', 'servers_to_use'));
        options['Energy']['freq_to_use'] = float(parser.get('Energy', 'freq_to_use')) * 10**9;
	options['Energy']['routing_option'] = str(parser.get('Energy', 'routing_option'))
	options['Energy']['dvfs_option'] = str(parser.get('Energy', 'dvfs_option'))
	
	wake_up_dist_str = parser.get('Energy', 'wake_up_distribution')
	wake_up_kwargs = ast.literal_eval(parser.get('Energy', 'wake_up_kwargs'))
	arrival_dist_str = parser.get('Energy', 'arrival_distribution')
	arrival_kwargs = ast.literal_eval(parser.get('Energy', 'arrival_kwargs'))

	if arrival_dist_str == 'exponential':
		options['Energy']['arrival_distribution'] = np.random.exponential
		options['arrival_rate'] = ((1 * 10**3) / arrival_kwargs['scale'])
	elif arrival_dist_str == 'pareto':
		options['Energy']['arrival_distribution'] = scipy.stats.pareto.rvs
		options['arrival_rate'] = ((1 * 10**3) / (arrival_kwargs['scale'] * arrival_kwargs['b'] / (arrival_kwargs['b'] - 1)))
	elif arrival_dist_str == 'lognormal':
		options['Energy']['arrival_distribution'] = np.random.lognormal
	elif arrival_dist_str == 'fixed':
		options['Energy']['arrival_distribution'] = np.random.choice
		options['arrival_rate'] = ((1 * 10**3) / arrival_kwargs['a'])
	elif arrival_dist_str == 'poisson':
		options['Energy']['arrival_distribution'] = np.random.poisson
		options['arrival_rate'] = ((1 * 10**3) / arrival_kwargs['lam'])

	if wake_up_dist_str == 'exponential':
		options['Energy']['wake_up_distribution'] = np.random.exponential
	elif wake_up_dist_str == 'pareto':
		options['Energy']['wake_up_distribution'] = scipy.stats.pareto.rvs
	elif wake_up_dist_str == 'lognormal':
		options['Energy']['wake_up_distribution'] = np.random.lognormal
	elif wake_up_dist_str == 'fixed':
		options['Energy']['wake_up_distribution'] = np.random.choice
	elif wake_up_dist_str == 'poisson':
		options['Energy']['wake_up_distribution'] = np.random.poisson

	options['Energy']['arrival_dist_str'] = arrival_dist_str
	options['Energy']['arrival_kwargs'] = arrival_kwargs
	options['Energy']['wake_up_dist_str'] = wake_up_dist_str
	options['Energy']['wake_up_kwargs'] = wake_up_kwargs
	
	if (len(sys.argv) == 3):
		# read the whole file line by line
		with open(sys.argv[2]) as f:
			options['Energy']['real_data'] = f.readlines()

		# get rid of all the new lines
		options['Energy']['real_data'] = [float(x.strip()) for x in options['Energy']['real_data']]
	else:
		options['Energy']['real_data'] = list()

	return options
