from __future__ import division
from ServerStates import State
from Queue import Queue
from simenv import get_env
import numpy as np

class ProcessHost:
    def __init__(self, hostid, config, req_size, freq, max_freq, arrival_dist, arrival_kwargs, arrival_rate, wake_up_dist, wake_up_kwargs, dvfs_option):
        # class variables
        self.id = hostid
        self.timescale = config['timescale']
        self.comp_time = (self.timescale * req_size) / freq
        self.req_size = req_size
        self.fixed_freq = self.freq = freq
        self.max_freq = max_freq
        self.arrival_dist = arrival_dist
        self.arrival_kwargs = arrival_kwargs
        self.arrival_rate = arrival_rate
        self.wake_up_dist = wake_up_dist
        self.wake_up_kwargs = wake_up_kwargs
        self.state = State.SLEEP
        self.packets = Queue()
        self.start_timer = 0
        self.end_timer = 0
        self.dvfs_option = dvfs_option

        # data collection
        self.computing_times = list()
        self.wake_up_times = list()
        self.sleep_times = list()
        self.packet_latency = list()
        self.packet_comp_time = list()
        self.packet_freq_history = list()
        self.queue_size = dict()

    def __cmp__(self, other):
        # I don't think we use this anymore
        return cmp(self.packets.qsize(), other.packets.qsize())

    def process_service(self):
        env = get_env()

        while True:
            if (self.state == State.AWAKE):
                # only process if the server is awake
                if self.packets.qsize() == 0:
                    #empty queue
                    self.sleep_server(env)
                    continue
                else:
                    # determine computation time
                    comp_time = np.random.exponential(self.comp_time)
                    pkt = self.packets.get()
                    yield env.timeout(comp_time)

                    self.finish_packet(env, pkt, comp_time, self.freq)

                    freq = self.fixed_freq

                    if self.dvfs_option == 'rubik':
                        if self.packets.qsize() != 0:
                            for i in range(self.packets.qsize()):
                                time_spent_in_sys = (env.now - pkt.birth_tick) / self.timescale
                                temp_freq = (self.fixed_freq / 2) / (0.5 - time_spent_in_sys)

                                if temp_freq > freq:
                                    freq = temp_freq

                                freq = min(freq, self.max_freq)

                            self.comp_time = (self.timescale * self.req_size) / (freq)
                            self.freq = freq
            elif self.state == State.BOOTING:
                # we are booting, so we need to figure out for how long
                time_to_wake_up = self.wake_up_dist(**self.wake_up_kwargs)
                self.end_timer = env.now
                diff = self.end_timer - self.start_timer
                self.sleep_times.append(diff)
                self.wake_up_times.append(time_to_wake_up)
                yield env.timeout(time_to_wake_up)

                self.finish_booting_server(env, time_to_wake_up)
            else:
                # do nothing, we are already asleep
                time_to_wait = self.timescale / self.arrival_rate / 10
                yield env.timeout(time_to_wait)

    def finish_packet(self, env, pkt, comp_time, freq):
        full_processing_time = env.now - pkt.birth_tick
        self.packet_latency.append(full_processing_time)
        self.packet_comp_time.append(comp_time)
        self.packet_freq_history.append(freq)

    def wake_up_server(self, env):
        self.state = State.BOOTING

    def finish_booting_server(self, env, time_to_wake_up):
        self.start_timer = env.now
        self.state = State.AWAKE

    def sleep_server(self, env):
        self.end_timer = env.now
        diff = self.end_timer - self.start_timer
        self.start_timer = env.now
        self.computing_times.append(diff)
        self.state = State.SLEEP

    def end_sim(self, env):
        if self.state == State.SLEEP:
            self.end_timer = env.now
            diff = self.end_timer - self.start_timer
            self.start_timer = env.now
            self.sleep_times.append(diff)
            self.state = State.SLEEP
        else:
            self.sleep_server(env)
