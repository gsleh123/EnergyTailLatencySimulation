
import random
import simpy
import math

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
		self.current_temp = 30
		self.max_temp = 70
		#self.temp_increase_coef
		
	def packets_arrival(self, env):
		# packet arrivals 
		
		while True:
			# Infinite loop for generating packets
			arrival_rate = self.arrival_rate



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

	def adjust_temp():
		""" Implement the heat control/dissapation and
		CPU freq modifications here"""

		# TODO: remove hard-coded value
		num_of_samples = 32

		ewma = Packet_Delay.EWMA(num_of_samples)

		if ewma == None:
			return

		

