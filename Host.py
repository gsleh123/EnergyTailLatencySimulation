import logging
from simenv import get_env
import numpy as np
from collections import namedtuple
import itertools
import EnergyRunner as er
import PoissonAlgorithm as pa
import ProcessHost
import DistributionHost
import sys
from Queue import Queue

hosts = []

lognormal_param = namedtuple('lognormal_param', 'mean sigma')

def init_hosts(config):
    global hosts
    global num_of_hosts
    global main_host
	
    hosts = []
    num_of_hosts = 0
    report_type = config['mpip_report_type']
    timescale = config['timescale']

    # set up the distribution host
    arrival_distribution = config['Energy']['arrival_distribution']
    arrival_kwargs = config['Energy']['arrival_kwargs']
    arrival_rate = config['arrival_rate']
    alphaThresh = config['Energy']['alphaThresh']
    betaThresh = config['Energy']['betaThresh']
    routing_option = config['Energy']['routing_option']
    packet_window_size = config['Energy']['packet_window_size']

    # retrieve all the settings
    real_data = config['Energy']['real_data']
    wake_up_dist = config['Energy']['wake_up_distribution']
    wake_up_kwargs = config['Energy']['wake_up_kwargs']
    req_arr_rate = 1000 / np.mean(real_data) if len(real_data) != 0 else config['arrival_rate']
    req_size = config['req_size']

    sim_mode = config['Energy']['sim_mode']
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
	
    main_host = DistributionHost.DistributionHost(arrival_distribution, arrival_kwargs, arrival_rate, alphaThresh, betaThresh, routing_option, active_servers, d_0, timescale, e, packet_window_size)

    # determine optimal number of servers and optimal frequency
    dimension_depth = 2
    [num_of_hosts, freq] = pa.find_hosts(req_arr_rate, req_size, e, d_0, s_b, s_c, pow_con_model, k_m, b, P_s, alpha, num_of_servers, problem_type, freq_setting, servers_to_use, freq_to_use)

    # error
    if (num_of_hosts == -1):
        return 0
				
    for i in range(num_of_hosts):
        # instantiate a new host
	host = ProcessHost.ProcessHost(i, config, req_size, freq, max_freq, arrival_distribution, arrival_kwargs, arrival_rate, wake_up_dist, wake_up_kwargs, dvfs_option)
        hosts.append(host)

    env = get_env()
	
    if sim_mode == 'ipp':
        env.process(main_host.process_arrivals_ipp_mode())
        env.process(main_host.process_arrivals_ipp())
    elif sim_mode == 'real':
        if (len(real_data) != 0):
            env.process(main_host.process_arrivals_real(real_data))
        else:
            raise ValueError('No real data found')
    else:
        env.process(main_host.process_arrivals_theoretical())
	
    for i in np.random.permutation(num_of_hosts):
	env.process(hosts[i].process_service())

    target_timestep = config['timesteps']
		
    return get_env().process(er.EnergyRunner(target_timestep))

def get_hosts():
    global hosts
    return hosts
