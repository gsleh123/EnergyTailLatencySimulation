import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import Host


def SetupVis():
    sns.set_context("poster")


def ShowQueueLengthHistory():
    data = Host.hosts[0].packet_queuesize
    xmax = len(Host.hosts[0].packet_queuesize)
    ymax = max(Host.hosts[0].packet_queuesize)
    index = [i for i in range(xmax)]
    queuesize = pd.DataFrame({'Timestep':index, 'queuesize': data})
    lm = sns.lmplot("Timestep", "queuesize", queuesize, size=7, aspect=3, fit_reg=False)
    ax = lm.axes
    ax[0, 0].set_xlim(0 - 0.05*xmax, 1.05*xmax)
    ax[0, 0].set_ylim(0 - 0.05*ymax, 1.1*ymax)
    plt.gcf().suptitle('Queue length over time', fontsize=24)
    plt.tight_layout()

    plt.show()
    plt.savefig("fig/QueueLengthHistory.png")


def ShowLatencyDist():
    # latencies of all hosts
    latencies_all = []

    print('%5s |%7s |%11s |%16s |%9s' % ('Host', 'PktCnt', 'AvgLatency', 'TailLatency-p98', 'EmptyCnt'))
    for i in range(Host.num_of_hosts):

        latencies = np.array(Host.hosts[i].latencies)
        latencies_all.extend(Host.hosts[i].latencies)

        # Note: qsize is only accurate if no other threads are accessing!
        print('%5i |%7i |%11.2f |%16.2f |%9i' % (i, Host.hosts[i].packet_queue.qsize(), np.mean(latencies),
                                                 np.percentile(latencies, 98), Host.hosts[i].empty_count))

    # Print totals
    print('%5s |%7i |%11.2f |%16.2f |%9i' % ('Total', sum([host.packet_queue.qsize() for host in Host.hosts]),
                                             np.mean(latencies_all), np.percentile(latencies_all, 98), sum([host.empty_count for host in Host.hosts])))

    # pprint(latencies_all)
    sns.distplot(latencies_all, norm_hist=True)
    plt.tight_layout()

    plt.show()
    plt.savefig("fig/LatencyDist.png")


def ShowFreqHistory():
    df = pd.DataFrame(columns=['Timestep', 'Frequency', 'Host'])
    for h in Host.hosts:
        to_insert = [[i, h.freq_history[i], h.id] for i in range(len(h.freq_history))]
        df = df.append(pd.DataFrame(to_insert, columns=['Timestep', 'Frequency', 'Host']))

    lm = sns.lmplot(x='Timestep', y='Frequency', hue='Host', data=df, fit_reg=False, size=7, aspect=3)
    xmax = max(df['Timestep'])
    ymax = max(df['Frequency'])
    ax = lm.axes
    ax[0, 0].set_xlim(0 - 0.1*xmax, 1.1*xmax)
    ax[0, 0].set_ylim(0 - 0.1*ymax, 1.1*ymax)
    plt.gcf().suptitle('Frequency over time', fontsize=24)
    plt.tight_layout()

    plt.show()
    plt.savefig("fig/FreqHistory.png")
