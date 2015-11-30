
import random
import simpy
import math
import numpy as np
from collections import deque
from pprint import pprint

from Packet import Packet

""" Queue system  """
class Server:
	def __init__(self, env, arrival_rate, Packet_Delay,
		Server_Idle_Periods, base_service_time, base_clock_rate, increased_clock_rate):
		self.server = simpy.Resource(env, capacity = 1)
		self.env = env
		self.queue_len = 0
		self.flag_processing = 0
		self.packet_number = 0
		self.sum_time_length = 0
		self.start_idle_time = 0
		self.arrival_rate = arrival_rate
		self.Packet_Delay = Packet_Delay
		self.Server_Idle_Periods = Server_Idle_Periods
		
		self.base_service_time = base_service_time
		self.base_clock_rate = base_clock_rate
		self.increased_clock_rate = increased_clock_rate
		self.current_clock_rate = base_clock_rate

		self.resting_temp = 30.0
		self.current_temp = 30.0
		self.max_temp = 70.0
		self.recent_ewma = deque()
		self.burst_start = 0
		
	def packets_arrival(self, env):
		# packet arrivals 
		
		while True:
			# Infinite loop for generating packets
			arrival_rate = self.arrival_rate

			self.adjust_temp()

			yield env.timeout(random.expovariate(self.arrival_rate))
			# arrival time of one packet

			self.packet_number += 1
			# packet id
			arrival_time = env.now  
			new_packet = Packet(self.packet_number,arrival_time)
			if self.flag_processing == 0:
				self.flag_processing = 1
				idle_period = env.now - self.start_idle_time
				self.Server_Idle_Periods.addNumber(idle_period)
			self.queue_len += 1
			env.process(self.process_packet(env, new_packet))

	def process_packet(self, env, packet):
		with self.server.request() as req:
			start = env.now
			yield req
			service_time = self.base_service_time / (self.current_clock_rate / self.base_clock_rate)
			yield env.timeout(random.expovariate(service_time))
			latency = env.now - packet.arrival_time
			self.Packet_Delay.addNumber(latency)
			self.queue_len -= 1
			if self.queue_len == 0:
				self.flag_processing = 0
				self.start_idle_time = env.now

	def adjust_temp(self):
		""" Implement the heat control/dissapation and
		CPU freq modifications here"""

		# TODO: remove hard-coded value
		num_of_samples = 3

		ewma = self.Packet_Delay.EWMA(num_of_samples)

		if ewma == None:
			return

		self.recent_ewma.appendleft(ewma)

		# If we have less than num_of_samples^2, then skip
		# i.e. for 32 samples per ewma,
		# we want at least 1024 for calculating percentiles
		if len(self.recent_ewma) < num_of_samples**2:
			return

		# Maintain the queue size to num_of_samples^2
		self.recent_ewma.pop()

		if self.current_clock_rate == self.base_clock_rate:
			# Normal clock freq
			
			# This is the timing for the nth-percentile
			percentile_timing = np.percentile(np.array(self.recent_ewma), 90)

			# lower temp
			temp_decrease_coef = 1 + (self.base_clock_rate / self.increased_clock_rate) * self.Packet_Delay.dataset[-1]/1000
			self.current_temp = min(self.resting_temp, self.current_temp * temp_decrease_coef)

			if ewma > percentile_timing or self.current_temp >= self.max_temp:
				self.current_clock_rate = self.increased_clock_rate
				print("%3i clock increased. temp: %f" % (self.packet_number, self.current_temp))
				self.burst_start = self.packet_number

				if self.current_temp >= self.max_temp:
					print("Clock freq dropped due to high temp")

		elif self.current_clock_rate == self.increased_clock_rate:
			# Increased clock freq

			percentile_timing = np.percentile(np.array(self.recent_ewma), 20)

			# raise temp, scaling by most recent latency
			temp_increase_coef = 1 + (self.increased_clock_rate / self.base_clock_rate) * self.Packet_Delay.dataset[-1]/1000
			print("temp increased to %f" % (self.current_temp * temp_increase_coef))
			self.current_temp = self.current_temp * temp_increase_coef

			if ewma <= percentile_timing:
				self.current_clock_rate = self.base_clock_rate
				print("%3i clock decreased. temp: %i" % (self.packet_number, self.current_temp))

				print("Last burst lasted %i packets\n" % (self.packet_number - self.burst_start))

