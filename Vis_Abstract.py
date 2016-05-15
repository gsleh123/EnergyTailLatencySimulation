import logging
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import pandas as pd
import seaborn as sns
import Host
from simenv import get_env
import AbstractHost


def setup():
    sns.set_context('poster')
    sns.set_palette(sns.color_palette('Set2', 10))


def show_graphs(config):

    show_packet_lifetimes(config)

    pass


def show_packet_lifetimes(config):
    hosts = Host.get_hosts()

    fig, ax = plt.subplots(2, figsize=(15, 10), sharex=True)

    lifetimes = list()
    for host in hosts:
        lifetimes += host.packet_latency

    sns.distplot(ax=ax[0], a=lifetimes)
    ax[0].set_title('Packet Lifetime distribution')
    ax[0].set_xlabel('Lifetime (sim time)')
    ax[0].set_ylabel('Freq')

    sns.boxplot(ax=ax[1], data=lifetimes, orient='h')
    ax[1].set_title('Packet Lifetime Boxplot')

    plt.tight_layout()

    fig.text(0.6, 0.8, 'Arrival Dist: %s\n  Params: %s\nService Dist: %s\n  Params: %s' % (
        config['Abstract']['arrival_dist_str'], config['Abstract']['arrival_kwargs'],
        config['Abstract']['service_dist_str'], config['Abstract']['service_kwargs']))

    plt.show()
    plt.close()
