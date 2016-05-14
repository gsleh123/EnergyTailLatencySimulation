import logging
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

import Host
from simenv import get_env
import MILCHost

sample_rate = 1
qsize_over_time = pd.DataFrame(columns=['timestep', 'queuesize', 'hostid'])


def setup(rate):
    global sample_rate

    sns.set_context("poster")
    sns.set_palette(sns.color_palette("Set2", 10))

    sample_rate = rate


def show_graphs(config):
    # show_host_distributions(config)
    # show_host_range(config)
    # show_host_activity_gnatt(config)
    show_sampling_dist(config)


def show_host_distributions(config):
    hosts = Host.get_hosts()

    f, ax = plt.subplots(2, figsize=(12, 8))

    allreduce_bounds = [0, 0]
    isend_bounds = [0, 0]

    for host in hosts:
        allreduce_mean = host.allreduce_mean * config['timescalar']
        allreduce_sigma = host.allreduce_sigma * config['timescalar']
        # allreduce = np.random.lognormal(mean=allreduce_mean, sigma=allreduce_sigma, size=60)
        allreduce = np.random.normal(loc=allreduce_mean, scale=allreduce_sigma, size=60)
        sns.distplot(allreduce, hist=False, ax=ax[0])
        allreduce_bounds[0] = min([min(allreduce), allreduce_bounds[0]])
        allreduce_bounds[1] = max([max(allreduce), allreduce_bounds[1]])

        isend_mean = host.isend_mean * config['timescalar']
        isend_sigma = host.isend_sigma * config['timescalar']
        # isend = np.random.lognormal(mean=isend_mean, sigma=isend_sigma, size=60)
        isend = np.random.normal(loc=isend_mean, scale=isend_sigma, size=60)
        sns.distplot(isend, hist=False, ax=ax[1])
        isend_bounds[0] = min([min(isend), isend_bounds[0]])
        isend_bounds[1] = max([max(isend), isend_bounds[1]])

    allreduce_bounds[0] *= 0.9
    allreduce_bounds[1] *= 1.1
    isend_bounds[0] *= 0.9
    isend_bounds[1] *= 1.1

    ax[0].set_title('Rank MPI_AllReduce distributions')
    ax[0].set_xlabel('Time (us)')
    ax[0].set_ylabel('Frequency %')
    ax[0].set_xlim(allreduce_bounds)

    ax[1].set_title('Rank MPI_ISend distributions')
    ax[1].set_xlabel('Time (us)')
    ax[1].set_ylabel('Frequency %')
    ax[1].set_xlim(isend_bounds)

    plt.tight_layout()
    plt.show()
    plt.close()


def show_host_range(config):
    isend_distributions, allreduce_distributions, service_lognormal_param, raw_data = Host.__load_mpip_report(config)

    f, ax = plt.subplots(2, figsize=(42, 38))

    allreduce_min = list()
    allreduce_max = list()
    isend_min = list()
    isend_max = list()
    allreduce_means = list()
    isend_means = list()

    for host_id in raw_data.keys():
        h_allreduce = raw_data[host_id]['allreduce']
        h_isend = raw_data[host_id]['isend']

        # apply the reverse-scaling
        h_allreduce = [v / config['timescalar'] / 1000 for v in h_allreduce]
        h_isend = [v / config['timescalar'] / 1000 for v in h_isend]

        allreduce_min.append(h_allreduce[0])
        allreduce_max.append(h_allreduce[2])

        isend_min.append(h_isend[0])
        isend_max.append(h_isend[2])

        allreduce_means.append(h_allreduce[1])
        isend_means.append(h_isend[1])

    ax[0].vlines(range(len(raw_data.keys())), allreduce_min, allreduce_max)
    ax[0].vlines(range(len(raw_data.keys())), allreduce_min, allreduce_max)

    ax[0].plot(allreduce_means, color='r')
    ax[1].plot(isend_means, color='r')

    ax[0].set_title('Allreduce')
    ax[0].set_xlabel('Host ID')
    ax[0].set_ylabel('Time (ms)')
    ax[0].set(yscale="log")

    ax[1].set_title('ISend')
    ax[1].set_xlabel('Host ID')
    ax[1].set_ylabel('Time (ms)')
    ax[1].set(yscale="log")

    # plt.show()
    plt.tight_layout()
    plt.savefig('fig/host_range.png')
    print 'host_range.png written'
    plt.close()

    f, ax = plt.subplots(2, figsize=(12, 8))
    # sns.violinplot(ax=ax[0], x=allreduce_min, color=sns.color_palette('husl')[1], bw=.01)
    sns.boxplot(ax=ax[0], x=allreduce_min, color=sns.color_palette('husl')[1])
    # sns.distplot(ax=ax[0], a=allreduce_min, color=sns.color_palette('husl')[1])
    # sns.violinplot(ax=ax[1], x=isend_min, color=sns.color_palette('husl')[2], bw=.01)
    sns.boxplot(ax=ax[1], x=isend_min, color=sns.color_palette('husl')[2])

    ax[0].set_title('Allreduce minimums')
    ax[0].set_xlabel('Time (ms)')

    ax[1].set_title('ISend minimums')
    ax[1].set_xlabel('Time (ms)')

    print 'Allreduce\'s Minimum Summary:'
    print 'min: %f | mean: %f | max: %f' % (min(allreduce_min), np.mean(allreduce_min), max(allreduce_max))

    print 'ISend\'s Minimum Summary:'
    print 'min: %f | mean: %f | max: %f' % (min(isend_min), np.mean(isend_min), max(isend_min))

    plt.tight_layout()
    plt.show()
    plt.close()


def show_host_activity_gnatt(config):
    hosts = Host.get_hosts()

    # todo: draw vert lines where timesteps occur

    host_ids = list()
    activity = list()
    act_start = list()
    act_end = list()

    f, ax = plt.subplots(1, figsize=(15, 12))
    ax.yaxis.grid(False)

    ax.set(axis_bgcolor='lightgray')

    # has the data on when the time step changes happened
    milc_timestep_changes = hosts[0].timestep_change_locations

    for host in hosts:
        host_ids.extend([host.id] * len(host.activity))
        activity.extend(host.activity)
        act_start.extend(host.act_start)
        act_end.extend(host.act_end)
        # since we dont capture the end for the final activity, add it here
        act_end.append(milc_timestep_changes[-1])

    palette = sns.color_palette('husl')
    palette[MILCHost.MILC_ACTIVITY_COMM_ISEND] = '#1b9e77'
    palette[MILCHost.MILC_ACTIVITY_COMM_ALLREDUCE] = '#d95f02'
    palette[MILCHost.MILC_ACTIVITY_COMPUTE] = '#7570b3'
    palette[MILCHost.MILC_ACTIVITY_WAIT] = (0.2, 0.2, 0.2)

    def col(activity_num):
        return [palette[val] for val in activity_num]

    line_collection = plt.hlines(host_ids, act_start, act_end, color='black')
    line_collection.set_linewidth(8)

    line_collection = plt.hlines(host_ids, act_start, act_end, colors=col(activity))
    line_collection.set_linewidth(6)

    axes = ax

    axes.set_xlim([min(act_start) - max(act_end)*0.05, max(act_end)*1.05])
    axes.set_ylim([min(host_ids) - 1, max(host_ids) + 1])

    # draw vertical lines for timestep change locations
    for change_time in milc_timestep_changes:
        vert_line = plt.axvline(x=change_time, color=palette[5])
        vert_line.set_alpha(0.4)

    # draw alternating row backgrounds
    for i in range(0, len(hosts), 2):
        plt.axhspan(ymin=i-0.5, ymax=i+0.5, xmin=axes.get_xlim()[0], xmax=axes.get_xlim()[1]*10,
                    facecolor='0.3', alpha=0.2)

    # LEGEND
    milc_comm_isend_patch = mpatches.Patch(color=palette[MILCHost.MILC_ACTIVITY_COMM_ISEND],
                                           label='MILC_ACTIVITY_COMM_ISEND')
    milc_comm_allreduce_patch = mpatches.Patch(color=palette[MILCHost.MILC_ACTIVITY_COMM_ALLREDUCE],
                                               label='MILC_ACTIVITY_COMM_ALLREDUCE')
    milc_compute_patch = mpatches.Patch(color=palette[MILCHost.MILC_ACTIVITY_COMPUTE],
                                        label='MILC_ACTIVITY_COMPUTE')
    milc_wait_patch = mpatches.Patch(color=palette[MILCHost.MILC_ACTIVITY_WAIT],
                                     label='MILC_ACTIVITY_WAIT')

    box = axes.get_position()
    axes.set_position([box.x0, box.y0 + box.height * 0.1,
                       box.width, box.height * 0.9])

    plt.legend(handles=[milc_comm_isend_patch, milc_comm_allreduce_patch, milc_compute_patch, milc_wait_patch],
               loc='upper center', bbox_to_anchor=(0.5, -0.1),
               fancybox=True, shadow=True, ncol=5)
    # END LEGEND

    axes.set_title('Simulation Gnatt Chart')
    axes.set_xlabel('Simulation Time')
    axes.set_ylabel('Host ID')

    plt.tight_layout(rect=(-0, 0.1, 1, 1))
    plt.savefig('fig/sim_gnatt.png')
    plt.show()
    plt.close()


def show_sampling_dist(config):
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

    with open('data/node8_sample/samples.txt') as f_all:
        lines = f_all.readlines()

    isend = dict()
    allreduce = dict()

    isend_all = list()
    allreduce_all = list()

    isend_procs = dict()
    allreduce_procs = dict()

    for line in lines:
        data = line.split()
        host_id = int(data[0])
        type = data[1]

        proc = host_id // 32
        if not isend_procs.has_key(proc):
            isend_procs[proc] = list()
        if not allreduce_procs.has_key(proc):
            allreduce_procs[proc] = list()

        timing_data = map(int, data[2:])

        if type.startswith('a'):
            allreduce[host_id] = timing_data
            allreduce_all += timing_data
            allreduce_procs[proc] += timing_data
        elif type.startswith('i'):
            isend[host_id] = timing_data
            isend_all += timing_data
            isend_procs[proc] += timing_data

    logging.info('Sample Vis Data Loaded')

    colors = sns.color_palette()

    figsize = (35, 22)

    # the first row being all 32 cores, the second row being the combined
    # same for allreduce
    f_procs_isend, ax_procs_isend = plt.subplots(2, len(isend_procs), figsize=figsize, sharey=True)
    f_procs_allreduce, ax_procs_allreduce = plt.subplots(2, len(isend_procs), figsize=figsize, sharey=True)
    # timeseries
    f_ts, ax_ts = plt.subplots(2, figsize=figsize)
    f_bp, ax_bp = plt.subplots(2, figsize=figsize)
    f_all, ax_all = plt.subplots(2, figsize=figsize)

    f_procs_isend.suptitle('MPI_ISend by Node')
    f_procs_allreduce.suptitle('MPI_Allreduce by Node')
    f_ts.suptitle('MPI ISend/Allreduce over Time (Ranks 0,1,2)')
    f_bp.suptitle('MPI ISend/Allreduce Boxplot')
    f_all.suptitle('MPI ISend/Allreduce Distribution')

    # subplot titles
    ax_all[0].set_title('MPI_ISend (All Nodes)')
    ax_all[1].set_title('MPI_Allreduce (All Nodes)')

    ax_bp[0].set_title('MPI_ISend (All Nodes)')
    ax_bp[1].set_title('MPI_Allreduce (All Nodes)')

    ax_procs_isend[0, 0].set_ylabel('Time (us)')
    ax_procs_allreduce[0, 0].set_ylabel('Time (us)')
    ax_ts[0].set_xlabel('Sampling Index (Random Sampling 0.1%)')
    ax_ts[1].set_xlabel('Sampling Index (All Calls 100%)')
    ax_ts[0].set_ylabel('Call Time (us)')
    ax_ts[1].set_ylabel('Call Time (us)')
    ax_bp[0].set_ylabel('Call Time (us)')
    ax_bp[1].set_ylabel('Call Time (us)')
    ax_all[0].set_ylabel('Call Time Frequency')
    ax_all[1].set_ylabel('Call Time Frequency')

    bounds_isend = [0, np.percentile(isend_all, 99)]
    bounds_allreduce = [0, np.percentile(allreduce_all, 99)]

    for proc in range(len(isend_procs)):
        for core in range(32):
            host_id = proc*32 + core
            sns.distplot(ax=ax_procs_isend[0, proc], a=isend[host_id], hist=False)
            sns.distplot(ax=ax_procs_allreduce[0, proc], a=allreduce[host_id], hist=False)

            ax_procs_isend[0, proc].set_xlim(bounds_isend)
            ax_procs_allreduce[0, proc].set_xlim(bounds_allreduce)

        # timeseries
        for core in [0, 1, 2]:
            sns.tsplot(ax=ax_ts[0], data=isend[core], err_style=None, color=colors[core], alpha=0.4)
            sns.tsplot(ax=ax_ts[1], data=allreduce[core], err_style=None, color=colors[core], alpha=0.4)

        # all data combined
        sns.distplot(ax=ax_procs_isend[1, proc], a=isend_procs[proc])
        sns.distplot(ax=ax_procs_allreduce[1, proc], a=allreduce_procs[proc])
        ax_procs_isend[1, proc].set_xlim(bounds_isend)
        ax_procs_allreduce[1, proc].set_xlim(bounds_allreduce)

        # subplot titles
        ax_procs_isend[0, proc].set_title('Node %i MPI_ISend' % proc)
        ax_procs_allreduce[0, proc].set_title('Node %i MPI_Allreduce' % proc)

        ax_ts[0].set_title('MPI_ISend Timeseries (Host [0, 1, 2])')
        ax_ts[1].set_title('MPI_Allreduce Timeseries (Host [0, 1, 2])')

    sns.distplot(ax=ax_all[0], a=isend_all)
    sns.distplot(ax=ax_all[1], a=allreduce_all)

    sns.boxplot(ax=ax_bp[0], data=isend_all, orient='h')
    sns.boxplot(ax=ax_bp[1], data=allreduce_all, orient='h')

    layout_rect = (0, 0, 1, 0.95)

    f_procs_isend.tight_layout(rect=layout_rect)
    f_procs_allreduce.tight_layout(rect=layout_rect)
    f_ts.tight_layout(rect=layout_rect)
    f_bp.tight_layout(rect=layout_rect)
    f_all.tight_layout(rect=layout_rect)

    logging.info('Plotting done, saving figures')

    f_procs_isend.savefig('fig/MPI_ISend_by_node.png')
    f_procs_allreduce.savefig('fig/MPI_Allreduce_by_node.png')
    f_ts.savefig('fig/MPI_over_time.png')
    f_bp.savefig('fig/MPI_boxplot.png')
    f_all.savefig('fig/MPI_distribution.png')

    # f_procs_isend.subplots_adjust(top=0.85)
    # f_procs_allreduce.subplots_adjust(top=0.85)
    # f_ts.subplots_adjust(top=0.85)
    # f_bp.subplots_adjust(top=0.85)
    # f_all.subplots_adjust(top=0.85)

    plt.close()

    logging.info('Vis Done')


if __name__ == '__main__':
    setup(rate=1)
    show_graphs(config=None)  # todo: None is bad...
