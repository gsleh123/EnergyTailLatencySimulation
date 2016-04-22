import numpy as np
import itertools

newid = itertools.count().next


class Packet(object):
    def __init__(self):
        self.size = 1  # will be exponentially distributed in the future
        self.id = newid()
