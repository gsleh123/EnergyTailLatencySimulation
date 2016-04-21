import random
import logging
import numpy as np

import Host
from simenv import get_env
import Vis


def run(parser):

    env = get_env()

    required_options = ['freq_lower_bound', 'freq_upper_bound', 'arrival_rate', 'service_rate']
    for opt in required_options:
        if not parser.has_option('CC_Config', opt):
            print "Option", opt, "not found in config"
            return 1

    # if no seed present, use python's inbuilt generator
    if parser.has_option('CC_Config', 'seed'):
        seed = int(parser.get('CC_Config', 'seed'))
        random.seed(seed)
        np.random.seed(seed)

    freq_lower_bound = float(parser.get('CC_Config', 'freq_lower_bound'))
    freq_upper_bound = float(parser.get('CC_Config', 'freq_upper_bound'))
    arrival_rate = float(parser.get('CC_Config', 'arrival_rate'))
    service_rate = float(parser.get('CC_Config', 'service_rate'))

    sleep_alpha = 0
    if parser.has_option('CC_Config', 'sleep_alpha'):
        sleep_alpha = float(parser.get('CC_Config', 'sleep_alpha'))

    timesteps = 100
    if parser.has_option('CC_Config', 'timesteps'):
        timesteps = int(parser.get('CC_Config', 'timesteps'))

    num_of_hosts = 1
    if parser.has_option('CC_Config', 'host_count'):
        num_of_hosts = int(parser.get('CC_Config', 'host_count'))

    computation_communication_ratio = 0.5
    if parser.has_option('CC_Config', 'computation_communication_ratio'):
        computation_communication_ratio = int(parser.get('CC_Config', 'computation_communication_ratio'))

    mpip_report_type = ''
    if parser.has_option('CC_Config', 'mpip_report_type'):
        mpip_report_type = parser.get('CC_Config', 'mpip_report_type')

    env.process(track_progress(timesteps))

    Host.init_hosts(num_of_hosts, arrival_rate, service_rate, sleep_alpha, freq_lower_bound, freq_upper_bound,
                    computation_communication_ratio, mpip_report_type)
    Vis.setup(1)

    env.run(until=timesteps)

    logging.info('Simulation Complete')

    hosts = Host.get_hosts()
    for h in hosts:
        logging.info('Host %i has %i packets in queue', h.id, h.packets.qsize())

    Vis.show_graphs()


def track_progress(total_timesteps):
    env = get_env()
    completion_percentage = 0.
    while True:
        yield env.timeout(total_timesteps/10.)
        completion_percentage += 10
        print "%.0f%%" % completion_percentage

