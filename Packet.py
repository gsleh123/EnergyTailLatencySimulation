import numpy as np
import itertools

newid = itertools.count().next


class Packet(object):
    def __init__(self, birth_tick):
        self.size = 1  # will be exponentially distributed in the future
        self.id = newid()
        self.birth_tick = birth_tick
