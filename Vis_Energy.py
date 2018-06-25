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
	
        arr_times_mean = np.mean(Host.main_host.arrival_times)

	# get the tail latency
	lifetimes = list()

	for host in hosts:
		lifetimes += host.packet_latency

	dump_data = dict()
	dump_data['lifetimes'] = lifetimes
		
	# this determines which tail latencies violates the tail latency constraint
	temp = 0
	d_0 = config['Energy']['d_0'] * config['timescale']
	for lifetime in lifetimes:
		if lifetime > d_0:
			temp+=1
	
	if len(lifetimes) > 0:
		prob_lifetimes = temp / len(lifetimes)
	else:
		prob_lifetimes = 0
		
	# get the power usage settings
	num_of_servers = config['Energy']['num_of_servers']
	pow_con_model = config['Energy']['pow_con_model']
	b = config['Energy']['b']
	P_s = config['Energy']['P_s']
	k_m = config['Energy']['k_m'] / 10**9
	s_b = config['Energy']['s_b'] / 10**9
	problem_type = config['Energy']['problem_type']
	freq_setting = config['Energy']['freq_setting']
	
	servers_used = len(Host.hosts)
	total_comp_ratio = 0
        total_wake_up_ratio = 0
        total_sleep_ratio = 0
        total_power_usage = 0
        total_freq = 0
        count_freq = 0

	# calculate power usage
	for host in Host.hosts:
            freq = 0

            if sum(host.packet_latency) != 0:
		freq = (sum(x * y for x, y in zip(host.packet_freq_history, host.packet_latency)) / sum(host.packet_latency)) / (10**9)
		comp_power = ((freq - s_b) / k_m)**2 + b
                count_freq = count_freq + 1
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
	    total_comp_ratio = total_comp_ratio + comp_ratio
            total_wake_up_ratio = total_wake_up_ratio + wake_up_ratio
            total_sleep_ratio = total_sleep_ratio + sleep_ratio
            total_freq = total_freq + freq

        csv_temp_list = list()
        csv_temp_list.append(Host.main_host.num_packets / 7200)
        csv_temp_list.append(arr_times_mean)
        csv_temp_list.append(servers_used)
        csv_temp_list.append(total_freq / count_freq)
	csv_temp_list.append(total_comp_ratio / servers_used)
        csv_temp_list.append(total_wake_up_ratio / servers_used)
        csv_temp_list.append(total_sleep_ratio / servers_used)
        csv_temp_list.append(prob_lifetimes)
        csv_temp_list.append(total_power_usage)
		
	# write to a csv file 
	with open('simdata%d%dN=%sk=%s.csv' %(problem_type, freq_setting, num_of_servers, pow_con_model), 'ab') as csvfile:
		simdata = csv.writer(csvfile, delimiter=',')
		simdata.writerow(csv_temp_list)
