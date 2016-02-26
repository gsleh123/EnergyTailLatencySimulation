import json
import random

import numpy as np
import requests

# Simulation Classes
import Host
import Vis
from simenv import env

def Run(parser):

    global env

    required_options = ['freq_lower_bound', 'freq_higher_bound', 'arrival_rate', 'process_rate']
    for opt in required_options:
        if not parser.has_option('CC_Config', opt):
            print "Option", opt, "not found in config"
            return 1

    # if no seed present, use python's inbuilt generator
    if parser.has_option('CC_Config', 'seed'):
        seed = int(parser.get('CC_Config', 'seed'))
        random.seed(seed)
        np.random.seed(seed)

    freq_lower_bound    = float(parser.get('CC_Config', 'freq_lower_bound'))
    freq_higher_bound   = float(parser.get('CC_Config', 'freq_higher_bound'))
    arrival_rate        = float(parser.get('CC_Config', 'arrival_rate'))
    process_rate        = float(parser.get('CC_Config', 'process_rate'))

    sleep_alpha = 0
    if parser.has_option('CC_Config', 'sleep_alpha'):
        sleep_alpha = float(parser.get('CC_Config', 'sleep_alpha'))

    timesteps = 100
    if parser.has_option('CC_Config', 'timesteps'):
        timesteps = int(parser.get('CC_Config', 'timesteps'))

    num_of_hosts = 1
    if parser.has_option('CC_Config', 'host_count'):
        num_of_hosts = int(parser.get('CC_Config', 'host_count'))

    Host.init_hosts(num_of_hosts)

    for i in range(Host.num_of_hosts):
        Host.hosts.append(Host.Host(i, arrival_rate, process_rate, sleep_alpha, freq_lower_bound, freq_higher_bound))
        env.process(Host.hosts[i].packet_arrival())
        env.process(Host.hosts[i].packet_process())
        env.process(Host.hosts[i].enable_logging())
        env.process(Host.hosts[i].temp_tick())

    #env.process(UpdateWebStreamer())

    env.run(until=timesteps)

    print('done')

    Vis.SetupVis()
    
    Vis.ShowLatencyDist()
    Vis.ShowQueueLengthHistory()
    Vis.ShowFreqHistory()

def UpdateWebStreamer():
    global env

    url = "http://localhost:5656/update/hosts/0"

    while True:
        yield env.timeout(1000)

        data = {'val': [0]}
        for h in Host.hosts:
            data['val'].append(h.packet_queue.qsize())

        print json.dumps(data)

        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
