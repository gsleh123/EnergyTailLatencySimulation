
import random
from collections import deque
import numpy as np
from pprint import pprint
import simpy
import requests
import json
import pandas as pd

# plotting
import seaborn as sns
import matplotlib.pyplot as plt

from simenv import env
import Host
from Packet import Packet
from ThermalModel import ThermalSlack

# If true, turn off all freq change controls
CONTROL = False

random.seed(15)
np.random.seed(15)

def main():

    # print 'poisson'
    # for i in range(20):
    #   print np.random.poisson(lam=(100.))/10.
    # print 'exponential'
    # for i in range(20):
    #   print random.expovariate(0.1)

    # return

    global env

    arrival_rate = 8.5
    process_rate = 0.1
    sleep_alpha = 0.01


    Host.init_hosts()

    for i in range(Host.num_of_hosts):
        Host.hosts.append(Host.Host(i, arrival_rate, process_rate, sleep_alpha))
        env.process(Host.hosts[i].packet_arrival())
        env.process(Host.hosts[i].packet_process())
        env.process(Host.hosts[i].enable_logging())

    #env.process(UpdateWebStreamer())

    env.run(until=500000)

    print('done')

    sns.set_context("poster")

    #ShowLatencyDist()

    #for i in range(len(Host.hosts[1].self.packet_queuesize)):
    data = Host.hosts[0].packet_queuesize
    xmax = len(Host.hosts[0].packet_queuesize)
    ymax = max(Host.hosts[0].packet_queuesize)
    index = [i for i in range(xmax)]
    queuesize = pd.DataFrame({'Timestep':index, 'queuesize': data})
    lm = sns.lmplot( "Timestep", "queuesize", queuesize, size=7, aspect=3, fit_reg=False)
    ax = lm.axes
    ax[0,0].set_xlim(0 - 0.05*xmax, 1.05*xmax)
    ax[0,0].set_ylim(0 - 0.05*ymax, 1.1*ymax)
    plt.gcf().suptitle('Queue length over time', fontsize=24)
    plt.tight_layout()
    plt.show()

def ShowLatencyDist():
    # latencies of all hosts
    latencies_all = []

    print('%5s |%7s |%11s |%16s |%9s' % ('Host', 'PktCnt', 'AvgLatency', 'TailLatency-p98', 'EmptyCnt'))
    for i in range(Host.num_of_hosts):

        latencies = np.array(Host.hosts[i].latencies)
        latencies_all.extend(Host.hosts[i].latencies)

        # Note: qsize is only accurate if no other threads are accessing!
        print('%5i |%7i |%11.2f |%16.2f |%9i' % (i, Host.hosts[i].packet_queue.qsize(), np.mean(latencies), np.percentile(latencies, 98), Host.hosts[i].empty_count ))

    # Print totals
    print('%5s |%7i |%11.2f |%16.2f |%9i' % ('Total', sum([host.packet_queue.qsize() for host in Host.hosts]),
        np.mean(latencies_all), np.percentile(latencies_all, 98), sum([host.empty_count for host in Host.hosts]) ))

    #pprint(latencies_all)
    sns.distplot(latencies_all, norm_hist=True)
    plt.tight_layout()
    plt.show()


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


if __name__ == '__main__':
    main()
