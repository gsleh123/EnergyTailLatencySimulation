from ThermalModel import ThermalSlack
import numpy as np
from Queue import Queue
from simenv import env
from Packet import Packet
import random
import sys

num_of_hosts = 1

def init_hosts(numOfHosts):
    global hosts
    global num_of_hosts

    hosts = []
    num_of_hosts = numOfHosts

class Host(object):
    """docstring for Host"""
    def __init__(self, idd, arrival_rate, process_rate, sleep_alpha, freq_lower_bound, freq_higher_bound):
        self.id = idd
        self.arrival_rate = arrival_rate
        self.process_rate = process_rate
        self.sleep_alpha = sleep_alpha
        self.packet_queue = Queue()
        self.thermal_slack = ThermalSlack(freq_lower_bound, freq_higher_bound)

        self.packet_queue.put(Packet())

        ### Logging ###
        # latencies of all packets for this host
        self.latencies = []

        self.empty_count = 0
        self.packet_queuesize = []
        self.freq_history = []

    def packet_arrival(self):
        global env

        while True:
            yield env.timeout( np.random.poisson(lam=self.arrival_rate) )

            self.packet_queue.put(Packet())

            print "%i | New Packet arrival | queue size: %i" % (env.now , self.packet_queue.qsize())

            # time since the last packet arrived
            #time_diff = env.now - self.time_of_last_arrival
        
    def packet_process(self):
        global env

        while True:

            if self.packet_queue.empty():
                # nothing to do, keep sleeping
                yield env.timeout(1)
                #print "Queue empty"
                self.empty_count += 1
            else:
                # If freq is 0, we need to start up
                if self.thermal_slack.freq == 0 and self.sleep_alpha != 0.0:
                    # force a startup time wait before continuing
                    print "%i | Waking Up" % (env.now)
                    yield env.timeout(random.expovariate(self.sleep_alpha))
                    print "%i | Awakened" % (env.now)
                    self.thermal_slack.SetFreq(self.thermal_slack.lower_bound_freq)


                yield env.timeout(random.expovariate(self.process_rate)/self.thermal_slack.freq)
                pkt = self.packet_queue.get()

                print "%i | Serviced Packet | queue size: %i" % (env.now, self.packet_queue.qsize())

                time_taken = env.now - pkt.creation_time
                self.latencies.append(time_taken)

                # check if queue is empty. If so, go to sleep
                if self.packet_queue.empty():
                    self.thermal_slack.SetFreq(0)
                    print "%i | Sleeping" % (env.now)
    
    def enable_logging(self):
    	global env

    	while True:
    		yield env.timeout(1)

    		self.packet_queuesize.append(self.packet_queue.qsize())
    		self.freq_history.append(self.thermal_slack.freq)


    def temp_tick(self):
        global env

        while True:
            yield env.timeout(1)

            if not CONTROL:
                self.thermal_slack.Tick()
