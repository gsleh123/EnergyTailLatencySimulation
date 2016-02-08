
import numpy as np

class ThermalSlack(object):
	"""Acts like a buffer for modeling the thermal slack of a core"""
	def __init__(self):
		# The buffer will range from 0 to 100
		# 0 being resting temp, 100 being max allowed temp
		# The 0-1 scale is exponential
		self.buffer = 0
		self.freq = 1.2

		self.lower_bound_freq = 1.2
		self.higher_bound_freq = 3.0

	def Tick(self):
		""" We assume the heat generation is purely based on clock rate
		and nothing else"""

		if self.buffer == 0:
			return

		# Note: we could use a freq->temp map here instead of a formula
		# Assuming linear growth here
		temp_to_add = FreqToTempIncrease(self.freq)

		if self.buffer + temp_to_add > 100:
			# We cannot run this tick at this temp,
			# since it would overflow the thermal buffer
			# Instead run at base clock
			self.freq = self.base_freq
			temp_to_add = FreqToTempIncrease(self.freq)

		# We are in a temp-reduction frequency
		if temp_to_add < 0:
			self.buffer += temp_to_add

			if self.buffer < 0:
				self.buffer = 0

		else:
			# We know the temp is not enough to overflow
			self.buffer += temp_to_add

		print('tick')

	def SetFreq(self, new_freq):
		self.freq = new_freq

	def FreqToTempIncrease(self, freq):
		return np.interp(freq, [self.lower_bound_freq, self.higher_bound_freq][1,10])


