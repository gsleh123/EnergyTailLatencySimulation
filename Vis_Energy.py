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

def setup():
	sns.set_context('poster')
	sns.set_palette(sns.color_palette('Set2', 10))
	
def show_graphs(config):
	show_packet_lifetimes(config)
	
	pass

def show_packet_lifetimes(config):
	hosts = Host.get_hosts()

	lifetimes = list()

	for host in hosts:
		lifetimes += host.packet_latency

	dump_data = dict()
	dump_data['lifetimes'] = lifetimes
		
	temp = 0
	for lifetime in lifetimes:
		if lifetime > 10:
			temp+=1
	
	if len(lifetimes) > 0:
		prob_lifetimes = temp / len(lifetimes)
	else:
		prob_lifetimes = 0
		
	Host.csv_temp_list.append(prob_lifetimes)
	
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
