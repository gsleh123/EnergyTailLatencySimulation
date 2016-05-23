import random
import logging
import numpy as np
import time
import scipy.stats
import ast

import Host
from simenv import get_env
import Vis_MILC
import Vis_Abstract


def run(parser):
    env = get_env()

    config = create_config_dict(parser)

    config['timescalar'] = 1/1.
    report_type = config['mpip_report_type']

    proc = Host.init_hosts(config)

    if report_type == 'MILC':
        Vis_MILC.setup(rate=1)
    elif report_type == 'Abstract':
        Vis_Abstract.setup()

    time.sleep(1)

    logging.info('Simulation Started')

    env.run(proc)

    logging.info('Simulation Complete')

    if report_type == 'MILC':
        Vis_MILC.show_graphs(config)
    elif report_type == 'Abstract':
        Vis_Abstract.show_graphs(config)


def create_config_dict(parser):
    # we use a dict to pass the options around
    options = dict()

    required_options = ['freq_lower_bound', 'freq_upper_bound', 'arrival_rate', 'service_rate']
    for opt in required_options:
        if not parser.has_option('CC_Config', opt):
            print "Option", opt, "not found in config"
            return 1
        options[opt] = parser.get('CC_Config', opt)

    # if no seed present, use python's inbuilt generator
    if parser.has_option('CC_Config', 'seed'):
        seed = int(parser.get('CC_Config', 'seed'))
        random.seed(seed)
        np.random.seed(seed)

    freq_lower_bound = float(parser.get('CC_Config', 'freq_lower_bound'))
    freq_upper_bound = float(parser.get('CC_Config', 'freq_upper_bound'))
    arrival_rate = float(parser.get('CC_Config', 'arrival_rate'))
    service_rate = float(parser.get('CC_Config', 'service_rate'))

    options['freq_lower_bound'] = freq_lower_bound
    options['freq_upper_bound'] = freq_upper_bound
    options['arrival_rate'] = arrival_rate
    options['service_rate'] = service_rate

    sleep_alpha = 0
    if parser.has_option('CC_Config', 'sleep_alpha'):
        sleep_alpha = float(parser.get('CC_Config', 'sleep_alpha'))
    options['sleep_alpha'] = sleep_alpha

    timesteps = 100
    if parser.has_option('CC_Config', 'timesteps'):
        timesteps = int(parser.get('CC_Config', 'timesteps'))
    options['timesteps'] = timesteps

    num_of_hosts = 1
    if parser.has_option('CC_Config', 'host_count'):
        num_of_hosts = int(parser.get('CC_Config', 'host_count'))
    options['host_count'] = num_of_hosts

    computation_comm_ratio = 0.5
    if parser.has_option('CC_Config', 'computation_comm_ratio'):
        computation_comm_ratio = float(parser.get('CC_Config', 'computation_comm_ratio'))
    options['computation_comm_ratio'] = computation_comm_ratio

    mpip_report_type = ''
    if parser.has_option('CC_Config', 'mpip_report_type'):
        mpip_report_type = parser.get('CC_Config', 'mpip_report_type')
    options['mpip_report_type'] = mpip_report_type

    if options['mpip_report_type'] == 'MILC':
        options['MILC'] = dict()
        # todo: check entry exists
        dimensions = parser.get('MILC', 'problem_dimensions')
        options['MILC']['dimensions'] = [int(i) for i in dimensions.split()]

    if options['mpip_report_type'] == 'Abstract':
        options['Abstract'] = dict()
        options['Abstract']['problem_type'] = int(parser.get('Abstract', 'problem_type'))

        arrival_dist_str = parser.get('Abstract', 'arrival_distribution')
        arrival_kwargs = ast.literal_eval(parser.get('Abstract', 'arrival_kwargs'))
        comm_dist_str = parser.get('Abstract', 'comm_distribution')
        comm_kwargs = ast.literal_eval(parser.get('Abstract', 'comm_kwargs'))

        if arrival_dist_str == 'exponential':
            options['Abstract']['arrival_distribution'] = np.random.exponential
        elif arrival_dist_str == 'pareto':
            options['Abstract']['arrival_distribution'] = scipy.stats.pareto.rvs
        elif arrival_dist_str == 'lognormal':
            options['Abstract']['arrival_distribution'] = np.random.lognormal
        elif arrival_dist_str == 'fixed':
            options['Abstract']['arrival_distribution'] = np.random.choice

        if comm_dist_str == 'exponential':
            options['Abstract']['comm_distribution'] = np.random.exponential
        elif comm_dist_str == 'pareto':
            options['Abstract']['comm_distribution'] = scipy.stats.pareto.rvs
        elif comm_dist_str == 'lognormal':
            options['Abstract']['comm_distribution'] = np.random.lognormal
        elif comm_dist_str == 'fixed':
            options['Abstract']['comm_distribution'] = np.random.choice

        options['Abstract']['arrival_dist_str'] = arrival_dist_str
        options['Abstract']['comm_dist_str'] = comm_dist_str
        options['Abstract']['arrival_kwargs'] = arrival_kwargs
        options['Abstract']['comm_kwargs'] = comm_kwargs

        # since it's not easy to get the mean of a random distribution,
        # we just sample and take the sample mean
        samples = options['Abstract']['comm_distribution'](size=200, **(options['Abstract']['comm_kwargs']))
        options['Abstract']['comp_time'] = np.mean(samples) * options['computation_comm_ratio']

    return options

