import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import Host
from simenv import get_env

sample_rate = 1
qsize_over_time = pd.DataFrame(columns=['timestep', 'queuesize', 'hostid'])


def setup(rate):
    global sample_rate

    sns.set_context("poster")
    sns.set_palette(sns.color_palette("Set2", 10))

    sample_rate = rate

    get_env().process(log())


def log():
    global qsize_over_time

    env = get_env()
    while True:
        yield env.timeout(1)

        hosts = Host.get_hosts()

        # qsize_over_time = qsize_over_time.append(pd.DataFrame({
        #     'timestep': [env.now] * len(hosts),
        #      'queuesize': [h.service_queue.qsize() for h in hosts],
        #      'hostid': [h.id for h in hosts]
        # }))


def show_graphs():
    # show_qsize_history()
    show_host_distributions()


def show_qsize_history():
    global qsize_over_time

    # print qsize_over_time
    #
    # # lm = sns.lmplot(x='timestep', y='queuesize', hue='hostid', data=qsize_over_time, fit_reg=False, size=7, aspect=3)
    # ts = sns.tsplot(data=qsize_over_time, time='timestep', value='queuesize', condition='hostid')
    # plt.gcf().suptitle('Queue length over time', fontsize=24)
    # plt.tight_layout()
    #
    # plt.show()


def show_host_distributions():
    hosts = Host.get_hosts()

    f, ax = plt.subplots(2, figsize=(12, 8))

    for host in hosts:
        allreduce_mean = host.allreduce_mean
        allreduce_sigma = host.allreduce_sigma
        allreduce = np.random.lognormal(mean=allreduce_mean, sigma=allreduce_sigma, size=100)
        sns.distplot(allreduce, hist=False, label='host %i' % host.id, ax=ax[0])

        isend_mean = host.isend_mean
        isend_sigma = host.isend_sigma
        isend = np.random.lognormal(mean=isend_mean, sigma=isend_sigma, size=100)
        sns.distplot(isend, hist=False, label='host %i' % host.id, ax=ax[1])

    ax[0].set_title('Rank MPI_AllReduce distributions')
    ax[0].set_xlabel('Time (ms)')
    ax[0].set_ylabel('Frequency %')
    ax[0].set_xlim([0, 35])

    ax[1].set_title('Rank MPI_ISend distributions')
    ax[1].set_xlabel('Time (us)')
    ax[1].set_ylabel('Frequency %')
    ax[1].set_xlim([1, 1.2])

    plt.tight_layout()
    plt.show()

