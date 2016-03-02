import random
import logging
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import Host
from simenv import get_env
import Vis


def Run(parser):

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

    Host.init_hosts(num_of_hosts, arrival_rate, service_rate, sleep_alpha, freq_lower_bound, freq_upper_bound)
    Vis.setup(1)

    env.run(until=timesteps)

    logging.info('Simulation Complete')

    hosts = Host.get_hosts()
    for h in hosts:
        logging.info('Host %i has %i packets in queue', h.id, h.packets.qsize())

    Vis.show_graphs()

