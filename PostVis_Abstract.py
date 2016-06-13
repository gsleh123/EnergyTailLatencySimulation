import logging
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import pickle
import os


def setup():
    sns.set_context('poster')
    sns.set_palette(sns.color_palette('Set1', 10))


def show_lifetimes():
    """
    Looks for all files in ./data/lifetimes and tries to unpickle them.
    Expects the unpicked object to be a list of floats represeting lifetimes
    The label will be the filename
    :return:
    """

    files = []
    for (dirpath, dirnames, filenames) in os.walk('data/lifetimes'):
        files.extend(filenames)
        break

    fig, ax = plt.subplots(2, sharex=True)

    lifetimes = dict()
    avg_freq = dict()
    tail_latency_95 = dict()
    tail_latency_98 = dict()

    # maps filenames to colors
    col_map = dict()
    col_index = 0

    for file in files:
        data = pickle.load(open('data/lifetimes/' + file, 'rb'))

        lifetimes[file] = data['lifetimes']
        avg_freq[file] = data['avg_freq']
        tail_latency_95[file] = np.percentile(data['lifetimes'], 95)
        tail_latency_98[file] = np.percentile(data['lifetimes'], 98)

        col_map[file] = sns.color_palette()[col_index]
        col_index += 1

    # sort by mean
    sorted_values = sorted(lifetimes.items(), key=lambda d: d[0][0])

    # dataframe wants them all the same size, so we trim to smallest value
    least_samples = min([len(f) for f in lifetimes.values()])

    for da in (sorted_values):
        filename = da[0]
        data_entry = da[1]

        slope = 3 / (tail_latency_98[filename] - tail_latency_95[filename])
        ax[0].plot([tail_latency_95[filename], tail_latency_98[filename]], [95, 98],
                   color=col_map[filename], label='%s | %f' %(filename, slope))
        lifetimes[filename] = lifetimes[filename][:least_samples]

    handles, labels = ax[0].get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    ax[0].legend(handles, labels)

    data = pd.DataFrame(lifetimes, columns=files)
    sns.boxplot(ax=ax[1], data=data, orient='h', whis=2)

    index = 0.0
    for file in reversed(files):
        freq = avg_freq[file]
        tail95 = tail_latency_95[file]
        tail98 = tail_latency_98[file]
        fig.text(0.6, 0.14 + index, "avg freq %.2f | 95%% = %.2f | 98%% = %.2f" % (freq, tail95, tail98))
        index += 0.065

    ax[0].set_ylabel('Percentile')
    ax[1].set_xlabel('Packet Life Timespan')

    plt.show()
    plt.close()

if __name__ == '__main__':
    setup()
    show_lifetimes()
