from __future__ import division
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import Host
from simenv import get_env
import AbstractHost
import networkx as nx
import pickle
import csv

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
	
	if len(lifetimes) > 0:
		prob_lifetimes = temp / len(lifetimes)
	else:
		prob_lifetimes = 0
		
	Host.csv_temp_list.append(prob_lifetimes)
	#print lifetimes
	#logging.info('Probability of lifetimes over 10ms: %f' %(prob_lifetimes))
	
	num_of_servers = config['Abstract']['num_of_servers']
	pow_con_model = config['Abstract']['pow_con_model']
	b = config['Abstract']['b']
	P_s = config['Abstract']['P_s']
	k_m = config['Abstract']['k_m'] / 10**9
	s_b = config['Abstract']['s_b'] / 10**9
	problem_type = config['Abstract']['problem_type']
	freq_setting = config['Abstract']['freq_setting']
	
	servers_used = Host.csv_temp_list[1]
	freq = Host.csv_temp_list[2]
	comp_ratio = Host.csv_temp_list[3]
	wake_up_ratio = Host.csv_temp_list[4]
	sleep_ratio = Host.csv_temp_list[5]
	
	if pow_con_model == 1:
		power_usage = 1;
	elif pow_con_model == 2:
		comp_power = ((freq - s_b) / k_m)**2 + b
		power_usage = (comp_power * comp_ratio + wake_up_ratio * P_s + sleep_ratio * P_s) * servers_used
		Host.csv_temp_list.append(power_usage)
		
	with open('simdata%d%dN=%sk=%s.csv' %(problem_type, freq_setting, num_of_servers, pow_con_model), 'ab') as csvfile:
		simdata = csv.writer(csvfile, delimiter=',')
		simdata.writerow(Host.csv_temp_list)
		
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
