import numpy as np
import itertools

newid = itertools.count().next


class Packet(object):
    def __init__(self, birth_tick, last_parent):
        """
        :param birth_tick: The env.now when this packet was created
        :param last_parent: The id of the host who sent this packet
        :return:
        """
        self.size = 1  # will be exponentially distributed in the future
        self.id = newid()
        self.birth_tick = birth_tick
        self.last_parent = last_parent
