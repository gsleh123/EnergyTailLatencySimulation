
import math
import numpy

class StatObject:
	def __init__(self):
		self.dataset =[]

	def addNumber(self,x):
		self.dataset.append(x)
	def sum(self):
		n = len(self.dataset)
		sum = 0
		for i in self.dataset:
			sum = sum + i
		return sum
	def mean(self):
		n = len(self.dataset)
		sum = 0
		for i in self.dataset:
			sum = sum + i
		return sum/n
	def maximum(self):
		return max(self.dataset)
	def minimum(self):
		return min(self.dataset)
	def count(self):
		return len(self.dataset)
	def median(self):
		self.dataset.sort()
		n = len(self.dataset)
		if n//2 != 0: # get the middle number
			return self.dataset[n//2]
		else: # find the average of the middle two numbers
			return ((self.dataset[n//2] + self.dataset[n//2 + 1])/2)
	def standarddeviation(self):
		temp = self.mean()
		sum = 0
		for i in self.dataset:
			sum = sum + (i - temp)**2
		sum = sum/(len(self.dataset) - 1)
		return math.sqrt(sum)

	def EWMA(self, sample_count):
		""" Calculates an Exponentially Weighed Moving Average
		Returns None if not enough samples"""
		
		if len(self.dataset) < sample_count:
			return None

		my_weights = []
		for b in range(sample_count):
			my_weights.append(2**b)

		# Get the last sample_count samples, weight using the generated weights
		return numpy.average(self.dataset[-sample_count:], weights=my_weights)

