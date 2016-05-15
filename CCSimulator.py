import random
import logging
import numpy as np
import time

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

    computation_communication_ratio = 0.5
    if parser.has_option('CC_Config', 'computation_communication_ratio'):
        computation_communication_ratio = float(parser.get('CC_Config', 'computation_communication_ratio'))
    options['computation_communication_ratio'] = computation_communication_ratio

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
        service_dist_str = parser.get('Abstract', 'service_distribution')

        if arrival_dist_str == 'exponential':
            options['Abstract']['arrival_distribution'] = np.random.exponential
            options['Abstract']['arrival_kwargs'] = {'scale': 10}
        elif arrival_dist_str == 'pareto':
            options['Abstract']['arrival_distribution'] = np.random.pareto
            options['Abstract']['arrival_kwargs'] = {'shape': 5}
        elif arrival_dist_str == 'lognormal':
            options['Abstract']['arrival_distribution'] = np.random.lognormal
            options['Abstract']['arrival_kwargs'] = {'mean': 5, 'sigma': 1}

        if service_dist_str == 'exponential':
            options['Abstract']['service_distribution'] = np.random.exponential
            options['Abstract']['service_kwargs'] = {'scale': 3}
        elif service_dist_str == 'pareto':
            options['Abstract']['service_distribution'] = np.random.pareto
            options['Abstract']['service_kwargs'] = {'shape': 5}
        elif service_dist_str == 'lognormal':
            options['Abstract']['service_distribution'] = np.random.lognormal
            options['Abstract']['service_kwargs'] = {'mean': 5, 'sigma': 1}

        options['Abstract']['arrival_dist_str'] = arrival_dist_str
        options['Abstract']['service_dist_str'] = service_dist_str

    return options

