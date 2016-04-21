import numpy as np
from Queue import Queue

class TrafficController:
    def __init__(self, arrival_rate, service_rate, sleep_alpha,
                 computation_communication_ratio, mpip_report_type):

        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.sleep_alpha = sleep_alpha

        self.packets_arrival = Queue()
        self.packets_service = Queue()

        self.true_next_incoming = self.next_incoming_simulated
        if mpip_report_type == 'MILC':
            self.true_next_incoming = self.next_incoming_mpip

    def queue_arrivals_empty(self):
        return self.packets_arrival.qsize() == 0

    def next_incoming(self):
        """
        Request the next packet
        :return:
        """
        return self.true_next_incoming()

    def next_incoming_simulated(self):
        """
        Full simulation. Sample from a pure distribution
        """
        # 1 / arrival_rate as input into exponential
        return np.random.exponential(scale=1. / self.arrival_rate)

    def next_incoming_mpip(self):
        """
        Sample using an mpip report
        """
        return 0

    def packet_post_process(self):
        """
        What to do after a packet is serviced
        :return:
        """
        pass

    def service_packet(self):
        """
        :return: How long to service packet for
        """
        return np.random.exponential(scale=1. / self.service_rate)
