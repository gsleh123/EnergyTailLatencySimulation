
import random
from collections import deque
import numpy as np
from pprint import pprint
import simpy
import requests
import json

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

def main():
    global env

    arrival_rate = 0.14
    process_rate = 0.1
    sleep_alpha = 0.5


    Host.init_hosts()

    for i in range(Host.num_of_hosts):
        Host.hosts.append(Host.Host(i, arrival_rate, process_rate, sleep_alpha))
        env.process(Host.hosts[-1].packet_arrival())
        env.process(Host.hosts[-1].packet_process())

    env.process(UpdateWebStreamer())

    env.run(until=50000)

    print('done')

    # # latencies of all hosts
    # latencies_all = []

    # print('%5s |%7s |%11s |%16s ' % ('Host', 'PktCnt', 'AvgLatency', 'TailLatency-p99'))
    # for i in range(num_of_hosts):

    #     latencies = np.array(hosts[i].latencies)
    #     latencies_all.extend(hosts[i].latencies)

    #     # Note: qsize is only accurate if no other threads are accessing!
    #     print('%5i |%7i |%11.2f |%16.2f ' % (i, hosts[i].packet_queue.qsize(), np.mean(latencies), np.percentile(latencies, 98) ))

    # # Print totals
    # print('%5s |%7i |%11.2f |%16.2f ' % ('Total', sum([host.packet_queue.qsize() for host in hosts]),
    #     np.mean(latencies_all), np.percentile(latencies_all, 98) ))

    # #pprint(latencies_all)
    # sns.distplot(latencies_all, norm_hist=True)
    # plt.tight_layout()
    # plt.show()


def UpdateWebStreamer():
    global env

    url = "http://localhost:5656/update/hosts/0"

    while True:
        yield env.timeout(100)

        data = {'val': [0]}
        for h in Host.hosts:
            data['val'].append(h.packet_queue.qsize())

        print json.dumps(data)

        response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))


if __name__ == '__main__':
    main()
