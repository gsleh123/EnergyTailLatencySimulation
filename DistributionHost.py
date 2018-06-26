from __future__ import division
from Queue import Queue
from simenv import get_env
from Packet import Packet
from ServerStates import State
import Host

class DistributionHost:
    def __init__(self, arrival_distribution, arrival_kwargs, arrival_rate, alphaThresh, betaThresh, routing_option, active_servers, d_0, timescale, e, packet_window_size):
        self.packets = Queue()
        self.arrival_dist = arrival_distribution
        self.arrival_kwargs = arrival_kwargs
        self.arrival_rate = arrival_rate
        self.alphaThresh = alphaThresh
        self.betaThresh = betaThresh
        self.num_packets = 0
        self.arrival_times = list()
        self.count = 0
        self.routing_option = routing_option
        self.active_servers = active_servers
        self.min_servers = active_servers
        self.packetCount = 0
        self.packetFlag = 0

        # only used for ipp traffic
        self.state = 1
        self.switch = False

        self.packet_window_size = packet_window_size
        self.timescale = timescale
        self.e = e
        self.d_0 = d_0 * self.timescale

    def process_arrivals_theoretical(self):
        env = get_env()

        while True:
            time_till_next_packet_arrival = self.arrival_dist(**self.arrival_kwargs)
            yield env.timeout(time_till_next_packet_arrival)
            self.arrival_times.append(time_till_next_packet_arrival)
            self.create_packet(env)
            self.num_packets = self.num_packets + 1

    def process_arrivals_ipp(self):
        env = get_env()
        arrival_rate = self.arrival_rate
        state = self.state
        constOffset = self.timescale / arrival_rate / self.timescale;
        alphaThresh = self.alphaThresh
        betaThresh = self.betaThresh
        k = alphaThresh / betaThresh
        time_to_switch = 0

        while True:
            state = self.state
            switch = self.switch

            if state == 0:
                # generate traffic really quickly
                time_to_wait = np.random.exponential(self.timescale / arrival_rate * (1 / (1 + alphaThresh/betaThresh)))

                yield env.timeout(time_to_wait)
            else:
                time_till_next_packet_arrival = np.random.exponential(self.timescale/arrival_rate * (1 / (1  + alphaThresh/betaThresh)))
                yield env.timeout(time_till_next_packet_arrival)

                self.arrival_times.append(time_till_next_packet_arrival)
                self.create_packet(env)
                self.num_packets = self.num_packets + 1

    def process_arrivals_ipp_mode(self):
        env = get_env()

        while True:
            state = self.state

            if state == 0:
                time_to_switch = np.random.exponential(1 / self.betaThresh)
            else:
                time_to_switch = np.random.exponential(1 / self.alphaThresh)

            yield env.timeout(time_to_switch)

            if (self.state == 1):
                self.state = 0
            else:
                self.state = 1

    def process_arrivals_real(self, real_traffic):
        env = get_env()

        while True:
            time_till_next_packet_arrival = real_traffic[self.count]
            self.count = self.count + 1

            if self.count == len(real_traffic):
                self.count = 0

            yield env.timeout(time_till_next_packet_arrival)
            self.arrival_times.append(time_till_next_packet_arrival)
            self.num_packets = self.num_packets + 1
            self.create_packet(env)

    def create_packet(self, env):
        # determine which host to send the packet to
        i = 0
        #print(self.active_servers)
        if self.routing_option == 'min_queue_length':
            min_queue_len = float("inf")
            for x in range(self.active_servers):
                queue_len = Host.hosts[x].packets.qsize()
                if queue_len < min_queue_len:
                    i = x
                    min_queue_len = queue_len
        else:
            i = random.randint(0, self.active_servers - 1)

        #create packet
        pkt = Packet(env.now, Host.hosts[i].packets.qsize())

        #place packet in the queue
        Host.hosts[i].packets.put(pkt)

        # wake up server if we found it to be sleeping
        if Host.hosts[i].state == State.SLEEP:
            Host.hosts[i].wake_up_server(env)

        if self.packetFlag:
            self.packetCount = self.packetCount + 1

            if self.packetCount >= int(self.packet_window_size):
                self.packetFlag = 0

        total_latency = list()
        for x in range(self.active_servers):
            packet_latency_len = min(len(Host.hosts[i].packet_latency), int((self.packet_window_size / self.active_servers) + 1))
            total_latency = total_latency + Host.hosts[i].packet_latency[-packet_latency_len:]

        if len(total_latency) >= int(self.packet_window_size)  and not self.packetFlag:
            temp = 0
            d_0 = self.d_0

            for latency in total_latency:
                if latency > d_0:
                    temp+=1

            if len(total_latency) > 0:
                prob_lifetimes = temp / len(total_latency)
            else:
                prob_lifetimes = 0

            if prob_lifetimes > self.e:
                max_servers = len(Host.hosts)
                self.active_servers = min(self.active_servers + 1, max_servers)
                self.packetFlag = 1
                self.packetCount = 0
            else:
                min_servers = self.min_servers
                self.active_servers = max(self.active_servers - 1, min_servers)

