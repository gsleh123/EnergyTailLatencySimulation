import random
import logging
import numpy as np
import time

import Host
from simenv import get_env
import Vis


def run(parser):
    env = get_env()

    config = create_config_dict(parser)

    config['timescalar'] = 1/1000.

    proc = Host.init_hosts(config)
    Vis.setup(rate=1)

    time.sleep(1)

    env.run(proc)

    logging.info('Simulation Complete')

    Vis.show_graphs(config)


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
        print options['MILC']['dimensions'] 

    return options

