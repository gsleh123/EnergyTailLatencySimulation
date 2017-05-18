from __future__ import division
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

	#print 'starting graphs'

	show_packet_lifetimes(config)
	#show_wake_up_servers(config)
	
	pass

def show_packet_lifetimes(config):
	hosts = Host.get_hosts()

	#fig, ax = plt.subplots(2, figsize=(15, 10), sharex=True)

	lifetimes = list()

	# calculate average freq
	all_freq = []

	for host in hosts:
		lifetimes += host.packet_latency
		all_freq.extend(host.freq_history)

	#avg_freq = np.mean(all_freq)

	dump_data = dict()
	dump_data['lifetimes'] = lifetimes
	#dump_data['avg_freq'] = avg_freq

	# Does this fail if there is no lifetimes folder?
	#pickle.dump(dump_data, open('data/lifetimes/lifetime.pickle', 'wb'))

	#sns.distplot(ax=ax[0], a=lifetimes)
	#problem_string = ""
	#problem_type = config['Abstract']['problem_type']

	#if problem_type == 1:
	#	problem_string = 'Scatter'
	#elif problem_type == 2:
	#	problem_string = 'Broadcast'
	#elif problem_type == 3:
	#	problem_string = 'Gather'

	#ax[0].set_title('Packet Lifetime distribution')
	#ax[0].set_ylabel('Freq')

	#sns.boxplot(ax=ax[1], data=lifetimes, orient='h')
	#ax[1].set_title('Packet Lifetime Boxplot')
	#ax[1].set_xlabel('Lifetime (sim time)')

	#plt.tight_layout()
	
	#avg_lifetimes = np.mean(lifetimes)
	#max_lifetimes = max(lifetimes)
	#min_lifetimes = min(lifetimes)
	
	temp = 0
	for lifetime in lifetimes:
		if lifetime > 10:
			temp+=1
	
	prob_lifetimes = temp / len(lifetimes)
	logging.info('Probability of lifetimes over 10ms: %f' %(prob_lifetimes))

	#fig.text(0.5, 0.7, 'average lifetime: %f\nmax lifetimes: %f\nmin lifetimes: %f\nprob_lifetimes: %f\n' %(avg_lifetimes, max_lifetimes, min_lifetimes, prob_lifetimes))

	#fig.text(0.5, 0.7, 'Freq Lower: %s\n Freq Upper: %s\n Comp Comm Ratio: %s\n Arrival Dist: %s\n  Params: %s\nService Dist: %s\n  Params: %s' % (
	#	config['freq_lower_bound'], config['freq_upper_bound'], config['computation_comm_ratio'],
	#	config['Abstract']['arrival_dist_str'], config['Abstract']['arrival_kwargs'],
	#	config['Abstract']['comm_dist_str'], config['Abstract']['comm_kwargs']))
	
	# This fails if there is no fig directory.
	#plt.savefig('fig/abstract_packet_lifetimes.png')

	#plt.show()
	#plt.close()
	
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
