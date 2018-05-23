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
import networkx as nx
import pickle
import csv
import pandas as pd

def setup():
	sns.set_context('poster')
	sns.set_palette(sns.color_palette('Set2', 10))
	
def show_graphs(config):
	show_packet_lifetimes(config)
	
	pass

def show_packet_lifetimes(config):
	hosts = Host.get_hosts()
	
	Host.csv_temp_list.append(Host.main_host.num_packets / 7200)

	# get the mean
        arr_times_mean = np.mean(Host.main_host.arrival_times)

	Host.csv_temp_list.append(arr_times_mean)

	# get the tail latency
	lifetimes = list()

	for host in hosts:
		lifetimes += host.packet_latency

	dump_data = dict()
	dump_data['lifetimes'] = lifetimes
		
	# this determines which tail latencies violates the tail latency constraint
	temp = 0
	d_0 = config['Energy']['d_0'] * 1000
	for lifetime in lifetimes:
		if lifetime > d_0:
			temp+=1
	
	if len(lifetimes) > 0:
		prob_lifetimes = temp / len(lifetimes)
	else:
		prob_lifetimes = 0
		
	Host.csv_temp_list.append(prob_lifetimes)
	
	# get the power usage settings
	num_of_servers = config['Energy']['num_of_servers']
	pow_con_model = config['Energy']['pow_con_model']
	b = config['Energy']['b']
	P_s = config['Energy']['P_s']
	k_m = config['Energy']['k_m'] / 10**9
	s_b = config['Energy']['s_b'] / 10**9
	problem_type = config['Energy']['problem_type']
	freq_setting = config['Energy']['freq_setting']
	
	servers_used = Host.csv_temp_list[1]
	freq = Host.csv_temp_list[2]
	comp_ratio = Host.csv_temp_list[3]
	wake_up_ratio = Host.csv_temp_list[4]
	sleep_ratio = Host.csv_temp_list[5]
	
	# calculate power usage
	if pow_con_model == 1:
		power_usage = 1;
	elif pow_con_model == 2:
	    total_power_usage = 0
	    for host in Host.hosts:
                if sum(host.packet_latency) != 0:
		    freq = (sum(x * y for x, y in zip(host.packet_freq_history, host.packet_latency)) / sum(host.packet_latency)) / (10**9)
		    comp_power = ((freq - s_b) / k_m)**2 + b
                else:
                    comp_power = 0

                total_time = sum(host.computing_times) + sum(host.wake_up_times) + sum(host.sleep_times)
                
                if total_time == 0:
                    power_usage = P_s
                else:
		    comp_ratio = sum(host.computing_times) / total_time
		    wake_up_ratio = sum(host.wake_up_times) / total_time
		    sleep_ratio = sum(host.sleep_times) / total_time
		    power_usage = (comp_power * comp_ratio + wake_up_ratio * P_s + sleep_ratio * P_s)

                total_power_usage = total_power_usage + power_usage
	
	    Host.csv_temp_list.append(total_power_usage)
		
	# write to a csv file 
	with open('simdata%d%dN=%sk=%s.csv' %(problem_type, freq_setting, num_of_servers, pow_con_model), 'ab') as csvfile:
		simdata = csv.writer(csvfile, delimiter=',')
		simdata.writerow(Host.csv_temp_list)
