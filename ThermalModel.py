

class ThermalSlack(object):
	"""Acts like a buffer for modeling the thermal slack of a core"""
	def __init__(self):
		# The buffer will range from 0 to 100
		# 0 being resting temp, 100 being max allowed temp
		# The 0-1 scale is exponential
		self.buffer = 0
		self.freq = 1.5

		# A master table for how fast a core heats/cools at various frequencies
		# index is frequency, value is a rate of heating/cooling (negative values = cooling)
		# This rate is relative to the 0-100 buffer rating per 1ms
		self.temp_table = dict()
		self.temp_table[1.5] = -2
		self.temp_table[2.0] = 5
		self.temp_table[2.5] = 15

		self.base_freq = 1.5
		self.increased_avg_freq = 2.0 # to handle increased average
		self.sudden_spike_freq = 2.5 # to handle increased std-dev

	def Tick(self):
		""" We assume the heat generation is purely based on clock rate
		and nothing else"""

		if self.buffer == 0:
			return

		temp_to_add = temp_table[self.freq]

		if self.buffer + temp_to_add > 100:
			# We cannot run this tick at this temp,
			# since it would overflow the thermal buffer
			# Instead run at base clock
			self.freq = self.base_freq
			temp_to_add = temp_table[self.base_freq]

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
		
		# make sure this freq exists in temp_table
		if new_freq not in temp_table:
			raise KeyError('No thermal entry for frequency %f' % (new_freq))

		self.freq = new_freq

