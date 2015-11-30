
import random
import simpy

from StatObject import StatObject
from Server import Server

class Simulator(object):
	"""docstring for Simulator"""
	def __init__(self, random_seed, sim_time, ):
		super(Simulator, self).__init__()

		self.sim_time = sim_time

		random.seed(random_seed)

		#print("Simple queue system model:mu = {0}".format(self.base_service_time))
		print ("{0:<9} {1:<9} {2:<9} {3:<9} {4:<9} {5:<9} {6:<9} {7:<9}".format(
        "Lambda", "Count", "Min", "Max", "Mean", "Median", "Sd", "Utilization"))
	
		
	def Run(self, service_time_base_mu):
		for arrival_rate in [0.8]:
			env = simpy.Environment()
			Packet_Delay = StatObject()
			Server_Idle_Periods = StatObject()
			base_clock_rate = 1.4
			increased_clock_rate = 2.8
			router = Server(env, arrival_rate, Packet_Delay,
				Server_Idle_Periods, service_time_base_mu,
				base_clock_rate, increased_clock_rate)
			env.process(router.packets_arrival(env))
			env.run(until=self.sim_time)
			print ("{0:<9.3f} {1:<9} {2:<9.3f} {3:<9.3f} {4:<9.3f} {5:<9.3f} {6:<9.3f} {7:<9.3f}".format(
				round(arrival_rate, 3),
				int(Packet_Delay.count()),
				round(Packet_Delay.minimum(), 3),
				round(Packet_Delay.maximum(), 3),
				round(Packet_Delay.mean(), 3),
				round(Packet_Delay.median(), 3),
				round(Packet_Delay.standarddeviation(), 3),
				round(1-Server_Idle_Periods.sum()/self.sim_time, 3)))
