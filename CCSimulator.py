
import simpy
import random
from collections import deque
import numpy as np
from Queue import Queue

# plotting
import seaborn as sns
import matplotlib.pyplot as plt

from ThermalModel import ThermalSlack

# If true, turn off all freq change controls
CONTROL = False

env = simpy.Environment()
hosts = []
num_of_hosts = 4

random.seed(14)

def main():
    global env

    for i in range(num_of_hosts):
        hosts.append(Host(i, 0.2, 0.1))
        env.process(hosts[-1].packet_arrival())
        env.process(hosts[-1].packet_process())

    env.run(until=10000)

    print('done')

    # latencies of all hosts
    latencies_all = []

    print('%5s |%7s |%11s |%16s ' % ('Host', 'PktCnt', 'AvgLatency', 'TailLatency-p99'))
    for i in range(num_of_hosts):

    	latencies = np.array(hosts[i].latencies)
    	latencies_all.extend(hosts[i].latencies)

        # Note: qsize is only accurate if no other threads are accessing!
        print('%5i |%7i |%11.2f |%16.2f ' % (i, hosts[i].packet_queue.qsize(), np.mean(latencies), np.percentile(latencies, 99) ))

    # Print totals
    print('%5s |%7i |%11.2f |%16.2f ' % ('Total', sum([host.packet_queue.qsize() for host in hosts]),
    	np.mean(latencies_all), np.percentile(latencies_all, 99) ))


    sns.distplot(latencies_all, norm_hist=True)
    plt.tight_layout()
    plt.show()

class Host(object):
    """docstring for Host"""
    def __init__(self, idd, arrival_rate, process_rate):
        self.id = idd
        self.arrival_rate = arrival_rate
        self.process_rate = process_rate
        self.packet_queue = Queue()
        self.thermal_slack = ThermalSlack()

        self.time_of_last_arrival = 0
        # exponentially weighted rolling average of packet arrival rate
        self.ewra = 0
        # a coefficient for the ewra between 0-1
        # higher values = more influence on the current measurement
        # lower values = history keeps impact longer
        # this method uses the entire history (through the current mean)
        # but the number of effective samples is approximated as N = alpha^(-1)
        # reference: http://stats.stackexchange.com/a/44651
        self.ewra_alpha = 0.1

        # TODO: softcode the maxlen
        # this is a circular buffer for storing past ewra values
        # these will be used to calculate percentiles
        # maxlen=50 means the ewra at the last 50 arrivals will be used
        self.ewra_samples = deque([], maxlen = 50)

        # latencies of all packets for this host
        self.latencies = []

    def packet_arrival(self):
        global env

        while True:
            yield env.timeout(random.expovariate(self.arrival_rate))

            self.packet_queue.put(Packet())

            # time since the last packet arrived
            time_diff = env.now - self.time_of_last_arrival

            # decide if we should adjust the frequency
            # the thermal slack class will downclock if needed (due to temp)
            
            self.ewra = self.ewra + self.ewra_alpha*(time_diff - self.ewra)

            if len(self.ewra_samples) == 0:
                self.ewra_samples.append(self.ewra)
                continue

            if CONTROL:
            	pass
            else:
	            if self.thermal_slack.freq == self.thermal_slack.base_freq:

	                if self.ewra > np.percentile(self.ewra_samples, 80):
	                    self.thermal_slack.freq = self.thermal_slack.sudden_spike_freq
	                #elif self.ewra_samples[0:50/2]

	            else: # we are at a frequency higher than base

	                # if we are at less than 40th percentile, downclock
	                if self.ewra < np.percentile(self.ewra_samples, 40):
	                    self.thermal_slack.freq = self.thermal_slack.base_freq

            self.ewra_samples.append(self.ewra)
        
    def packet_process(self):
        global env

        while True:

        	if self.packet_queue.empty():
        		yield env.timeout(1)
        	else:
	            yield env.timeout(random.expovariate(self.process_rate)/self.thermal_slack.freq)
	            pkt = self.packet_queue.get()

	            time_taken = env.now - pkt.creation_time
	            self.latencies.append(time_taken)
            

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
