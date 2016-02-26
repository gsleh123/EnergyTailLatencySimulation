import numpy as np


class ThermalSlack(object):
    """Acts like a buffer for modeling the thermal slack of a core"""

    def __init__(self, freq_lower_bound, freq_higher_bound):
        # The buffer will range from 0 to 100
        # 0 being resting temp, 100 being max allowed temp
        # The 0-1 scale is exponential
        self.buffer = 0
        self.freq = freq_lower_bound

        self.lower_bound_freq = freq_lower_bound
        self.higher_bound_freq = freq_higher_bound

    def Tick(self):
        """ We assume the heat generation is purely based on clock rate
        and nothing else"""

        self.buffer += self.FreqToTempIncrease(self.freq)

        self.buffer = max(0, self.buffer)
        if self.buffer >= 100:
            self.freq = self.lower_bound_freq


    def SetFreq(self, new_freq):
        self.freq = new_freq
        self.freq = max(0, self.freq)
        self.freq = min(self.higher_bound_freq, self.freq)
        print "Changing freq to %f" % self.freq

    def FreqToTempIncrease(self, freq):

        print "Freq change:", freq, np.interp(freq, [self.lower_bound_freq, self.higher_bound_freq], [-2, 10]), self.buffer
        return np.interp(freq, [self.lower_bound_freq, self.higher_bound_freq], [-2, 10])
        return 0
