
import simpy
import random
from collections import deque
import numpy as np
from Queue import Queue
from pprint import pprint

# plotting
import seaborn as sns
import matplotlib.pyplot as plt

from ThermalModel import ThermalSlack

# If true, turn off all freq change controls
CONTROL = False

env = simpy.Environment()
hosts = []
num_of_hosts = 1

random.seed(14)

def main():
    global env

    arrival_rate = 0.11
    process_rate = 0.1
    sleep_alpha = 0.5

    for i in range(num_of_hosts):
        hosts.append(Host(i, arrival_rate, process_rate, sleep_alpha))
        env.process(hosts[-1].packet_arrival())
        env.process(hosts[-1].packet_process())

    env.run(until=50000)

    print('done')

    # latencies of all hosts
    latencies_all = []

    print('%5s |%7s |%11s |%16s ' % ('Host', 'PktCnt', 'AvgLatency', 'TailLatency-p99'))
    for i in range(num_of_hosts):

        latencies = np.array(hosts[i].latencies)
        latencies_all.extend(hosts[i].latencies)

        # Note: qsize is only accurate if no other threads are accessing!
        print('%5i |%7i |%11.2f |%16.2f ' % (i, hosts[i].packet_queue.qsize(), np.mean(latencies), np.percentile(latencies, 98) ))

    # Print totals
    print('%5s |%7i |%11.2f |%16.2f ' % ('Total', sum([host.packet_queue.qsize() for host in hosts]),
        np.mean(latencies_all), np.percentile(latencies_all, 98) ))

    #pprint(latencies_all)
    sns.distplot(latencies_all, norm_hist=True)
    plt.tight_layout()
    plt.show()

class Host(object):
    """docstring for Host"""
    def __init__(self, idd, arrival_rate, process_rate, sleep_alpha):
        self.id = idd
        self.arrival_rate = arrival_rate
        self.process_rate = process_rate
        self.sleep_alpha = sleep_alpha
        self.packet_queue = Queue()
        self.thermal_slack = ThermalSlack()

        # latencies of all packets for this host
        self.latencies = []

    def packet_arrival(self):
        global env

        while True:
            yield env.timeout(random.expovariate(self.arrival_rate))

            self.packet_queue.put(Packet())

            # time since the last packet arrived
            #time_diff = env.now - self.time_of_last_arrival
        
    def packet_process(self):
        global env

        while True:

            if self.packet_queue.empty():
                # nothing to do, keep sleeping
                yield env.timeout(1)
            else:
                # If freq is 0, we need to start up
                if self.thermal_slack.freq == 0:
                    # force a startup time wait before continuing
                    yield env.timeout(random.expovariate(self.sleep_alpha))
                    self.thermal_slack.SetFreq(self.thermal_slack.lower_bound_freq)


                yield env.timeout(random.expovariate(self.process_rate)/self.thermal_slack.freq)
                pkt = self.packet_queue.get()

                time_taken = env.now - pkt.creation_time
                self.latencies.append(time_taken)

                # check if queue is empty. If so, go to sleep
                if self.packet_queue.empty():
                    self.thermal_slack.SetFreq(0)
            

    def temp_tick(self):
        global env

        while True:
            yield env.timeout(1)

            if not CONTROL:
                self.thermal_slack.Tick()

class Packet(object):
    """docstring for Packet"""
    def __init__(self):
        global env
        
        self.creation_time = env.now
        

if __name__ == '__main__':
    main()
