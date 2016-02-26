
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

		if self.buffer == 0:
			return


	def SetFreq(self, new_freq):
		self.freq = new_freq

	def FreqToTempIncrease(self, freq):
		print freq, np.interp(freq, [self.lower_bound_freq, self.higher_bound_freq],[1,10])
		return np.interp(freq, [self.lower_bound_freq, self.higher_bound_freq],[1,10])


