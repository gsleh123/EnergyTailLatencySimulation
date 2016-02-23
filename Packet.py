from simenv import env

class Packet(object):
    """docstring for Packet"""
    def __init__(self):
        global env
        
        self.creation_time = env.now
        