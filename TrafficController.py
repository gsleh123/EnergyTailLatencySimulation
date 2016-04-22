from Queue import Queue
from simenv import get_env


class TrafficController:
    """
    An abstract class for different control schemes
    The packets are always kept with the Controller, never given to the hosts
    Note: Not using abc module, just skeleton functions
    """
    def __init__(self, config):
        raise NotImplementedError()

    def tick(self):
        raise NotImplementedError()

    def is_packet_waiting_for_arrival(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet waiting to 'arrive'
        """
        raise NotImplementedError()

    def receive_arrival_packet(self, host_id):
        """
        Request the next packet, Controller should remove from their arrival queue
        :param host_id: The id of the host requesting
        :return: None
        """
        raise NotImplementedError()

    def is_packet_waiting_for_service(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: True if there is a packet that needs to be serviced
        """
        raise NotImplementedError()

    def service_packet(self, host_id):
        """
        :param host_id: The id of the host requesting
        :return: How long to service packet for
        """
        raise NotImplementedError()