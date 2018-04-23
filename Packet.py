import numpy as np
import itertools

newid = itertools.count().next


class Packet(object):
    def __init__(self, birth_tick, queue_len):
        """
        :param birth_tick: The env.now when this packet was created
        :param last_parent: The id of the host who sent this packet
        :return:
        """
        self.birth_tick = birth_tick
	self.queue_len = queue_len
