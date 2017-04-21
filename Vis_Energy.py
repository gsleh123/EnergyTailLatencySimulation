import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import Host
from simenv import get_env
import AbstractHost
import networkx as nx
import pickle


def setup():
	sns.set_context('poster')
	sns.set_palette(sns.color_palette('Set2', 10))
	
def show_graphs(config):

	print 'starting graphs'

	#show_packet_lifetimes(config)
	show_wake_up_servers(config)
	
	pass
	
def show_wake_up_servers(config):
	hosts = Host.get_hosts()
	
	hosts_id = list() 
	hosts_awaken = list() 
	
	for host in hosts:
		hosts_id.append(host.id)
		hosts_awaken.append(len(host.wake_up_times))
	
	width = 1 / 1.5
	
	plt.bar(hosts_id, hosts_awaken, width)
	plt.xlabel('server id')
	plt.ylabel('# of times server is awaken')
	plt.title('Server Awaken')

	plt.show()