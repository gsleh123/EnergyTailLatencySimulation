import random
import logging
import numpy as np
import time
import scipy.stats
import ast
import Host
from simenv import get_env
import Vis_Energy

def run(parser):	
	config = create_config_dict(parser)
	
	config['timescalar'] = 1/1.
	report_type = config['mpip_report_type']

	env = get_env()
	proc = Host.init_hosts(config)
	
	if report_type == 'MILC':
		Vis_MILC.setup(rate=1)
	elif report_type == 'Abstract':
		Vis_Abstract.setup()
	elif report_type == 'Energy':
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
	
	#logging.info('Computing time: %f' %(total_computing_time / total_time))
	#logging.info('Wake up time: %f' %(total_wake_up_time / total_time))
	#logging.info('Sleep time: %f' %(total_sleep_time / total_time))
	
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

	options['Abstract'] = dict()
	options['Abstract']['problem_type'] = int(parser.get('Abstract', 'problem_type'))
	options['Abstract']['freq_setting'] = int(parser.get('Abstract', 'freq_setting'))

	options['Abstract']['d_0'] = float(parser.get('CC_Config', 'd_0'));
	options['Abstract']['P_s'] = int(parser.get('CC_Config', 'P_s'));
	options['Abstract']['alpha'] = int(parser.get('CC_Config', 'alpha'));
	options['Abstract']['num_of_servers'] = int(parser.get('CC_Config', 'num_of_servers'));
	options['Abstract']['e'] = float(parser.get('CC_Config', 'e'));
	options['Abstract']['s_b'] = float(parser.get('CC_Config', 's_b')) * 10**9;
	options['Abstract']['s_c'] = float(parser.get('CC_Config', 's_c')) * 10**9;
	options['Abstract']['pow_con_model'] = int(parser.get('CC_Config', 'pow_con_model'));
	options['Abstract']['k_m'] = float(parser.get('CC_Config', 'k_m')) * 10**9;
	options['Abstract']['b'] = int(parser.get('CC_Config', 'b'));

	wake_up_dist_str = parser.get('Abstract', 'wake_up_distribution')
	wake_up_kwargs = ast.literal_eval(parser.get('Abstract', 'wake_up_kwargs'))
	arrival_dist_str = parser.get('Abstract', 'arrival_distribution')
	arrival_kwargs = ast.literal_eval(parser.get('Abstract', 'arrival_kwargs'))

	if arrival_dist_str == 'exponential':
		options['Abstract']['arrival_distribution'] = np.random.exponential
		options['arrival_rate'] = ((1 * 10**3) / arrival_kwargs['scale'])
	elif arrival_dist_str == 'pareto':
		options['Abstract']['arrival_distribution'] = scipy.stats.pareto.rvs
	elif arrival_dist_str == 'lognormal':
		options['Abstract']['arrival_distribution'] = np.random.lognormal
	elif arrival_dist_str == 'fixed':
		options['Abstract']['arrival_distribution'] = np.random.choice
		options['arrival_rate'] = ((1 * 10**3) / arrival_kwargs['a'])
	elif arrival_dist_str == 'poisson':
		options['Abstract']['arrival_distribution'] = np.random.poisson
		options['arrival_rate'] = ((1 * 10**3) / arrival_kwargs['lam'])

	if wake_up_dist_str == 'exponential':
		options['Abstract']['wake_up_distribution'] = np.random.exponential
	elif wake_up_dist_str == 'pareto':
		options['Abstract']['wake_up_distribution'] = scipy.stats.pareto.rvs
	elif wake_up_dist_str == 'lognormal':
		options['Abstract']['wake_up_distribution'] = np.random.lognormal
	elif wake_up_dist_str == 'fixed':
		options['Abstract']['wake_up_distribution'] = np.random.choice
	elif wake_up_dist_str == 'poisson':
		options['Abstract']['wake_up_distribution'] = np.random.poisson

	options['Abstract']['arrival_dist_str'] = arrival_dist_str
	options['Abstract']['arrival_kwargs'] = arrival_kwargs
	options['Abstract']['wake_up_dist_str'] = wake_up_dist_str
	options['Abstract']['wake_up_kwargs'] = wake_up_kwargs
		
	return options

