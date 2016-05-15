import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import Host
from simenv import get_env
import AbstractHost
import networkx as nx

def setup():
    sns.set_context('poster')
    sns.set_palette(sns.color_palette('Set2', 10))


def show_graphs(config):

    show_network(config)
    # show_dist_pair(config)
    # show_packet_lifetimes(config)

    pass


def show_network(config):
    graph = nx.DiGraph()

    hosts = Host.get_hosts()

    for host in hosts:
        graph.add_node(host.id)

    for host in hosts:
        for dest in host.send_to:
            graph.add_edge(host.id, dest)

    fig = plt.figure(figsize=(20, 12))

    nx.draw_shell(graph, with_labels=True)

    plt.show()
    plt.close()


def show_dist_pair(config):

    fig, ax = plt.subplots(1)
    d1 = config['Abstract']['arrival_distribution'](size=100, **(config['Abstract']['arrival_kwargs']))
    d2 = config['Abstract']['comm_distribution'](size=100, **(config['Abstract']['comm_kwargs']))
    sns.distplot(d1, label='Arrival %s | %s' % (config['Abstract']['arrival_dist_str'], config['Abstract']['arrival_kwargs']))
    sns.distplot(d2, label='Comm %s | %s' % (config['Abstract']['comm_dist_str'], config['Abstract']['comm_kwargs']))

    ax.set_title('Arrival vs Communication Distributions')
    ax.set_xlabel('Sim Time')
    ax.set_ylabel('Freq')

    legend = plt.legend()

    plt.tight_layout()
    plt.show()
    plt.close()


def show_packet_lifetimes(config):
    hosts = Host.get_hosts()

    fig, ax = plt.subplots(2, figsize=(15, 10), sharex=True)

    lifetimes = list()
    for host in hosts:
        lifetimes += host.packet_latency

    sns.distplot(ax=ax[0], a=lifetimes)
    problem_string = ""
    problem_type = config['Abstract']['problem_type']

    if problem_type == 1:
        problem_string = 'Scatter'
    elif problem_type == 2:
        problem_string = 'Broadcast'
    elif problem_type == 3:
        problem_string = 'Gather'

    ax[0].set_title('Packet Lifetime distribution | %s' % problem_string)
    ax[0].set_ylabel('Freq')

    sns.boxplot(ax=ax[1], data=lifetimes, orient='h')
    ax[1].set_title('Packet Lifetime Boxplot')
    ax[1].set_xlabel('Lifetime (sim time)')

    plt.tight_layout()

    fig.text(0.6, 0.8, 'Arrival Dist: %s\n  Params: %s\nService Dist: %s\n  Params: %s' % (
        config['Abstract']['arrival_dist_str'], config['Abstract']['arrival_kwargs'],
        config['Abstract']['comm_dist_str'], config['Abstract']['comm_kwargs']))

    plt.show()
    plt.close()

