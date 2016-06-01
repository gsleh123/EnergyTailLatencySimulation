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
    tail_latency = dict()

    for file in files:
        data = pickle.load(open('data/lifetimes/' + file, 'rb'))

        lifetimes[file] = data['lifetimes']
        avg_freq[file] = data['avg_freq']
        tail_latency[file] = np.percentile(data['lifetimes'], 98)

    # sort by mean
    sorted_values = sorted(lifetimes.items(), key=lambda d: d[0][0])

    # dataframe wants them all the same size, so we trim to smallest value
    least_samples = min([len(f) for f in lifetimes.values()])

    for da in (sorted_values):
        filename = da[0]
        data_entry = da[1]

        sns.distplot(ax=ax[0], a=data_entry, hist=False, label=filename)
        lifetimes[filename] = lifetimes[filename][:least_samples]

    data = pd.DataFrame(lifetimes, columns=files)
    sns.boxplot(ax=ax[1], data=data, orient='h')

    index = 0.0
    for file in reversed(files):
        freq = avg_freq[file]
        tail = tail_latency[file]
        fig.text(0.7, 0.14 + index, "avg freq %f | 98%% = %f" % (freq, tail))
        index += 0.06

    plt.show()
    plt.close()

if __name__ == '__main__':
    setup()
    show_lifetimes()
