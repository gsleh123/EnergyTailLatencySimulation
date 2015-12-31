
import simpy
import random
from collections import deque
import numpy as np

from ThermalModel import ThermalSlack

env = simpy.Environment()
hosts = []
num_of_hosts = 4

def main():
    global env

    for i in range(num_of_hosts):
        hosts.append(Host(i, 0.1))
        env.process(hosts[-1].packet_arrival())
        env.process(hosts[-1].packet_process())

    env.run(until=100000)

    print('done')

    print('Host | PktCnt')
    for i in range(num_of_hosts):
        print('%i | %i' % (i, hosts[i].packet_queue))


class Host(object):
    """docstring for Host"""
    def __init__(self, idd, arrival_rate):
        self.id = idd
        self.arrival_rate = arrival_rate
        self.packet_queue = 0
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

    def packet_arrival(self):
        global env

        while True:
            yield env.timeout(random.expovariate(self.arrival_rate))

            self.packet_queue += 1

            # time since the last packet arrived
            time_diff = env.now - self.time_of_last_arrival

            # decide if we should adjust the frequency
            # the thermal slack class will downclock if needed (due to temp)
            
            self.ewra = self.ewra + self.ewra_alpha*(time_diff - self.ewra)

            if len(self.ewra_samples) == 0:
                self.ewra_samples.append(self.ewra)
                continue

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
            yield env.timeout(1)
            self.thermal_slack.Tick()


if __name__ == '__main__':
    main()
