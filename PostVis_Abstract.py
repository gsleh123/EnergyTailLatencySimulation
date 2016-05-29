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

    for file in files:
        data = pickle.load(open('data/lifetimes/' + file, 'rb'))

        sns.distplot(ax=ax[0], a=data, label=file)

        lifetimes[file] = data

    least_samples = min([len(f) for f in lifetimes.values()])
    for l in lifetimes:
        lifetimes[l] = lifetimes[l][:least_samples]

    data = pd.DataFrame(lifetimes, columns=files)
    sns.boxplot(ax=ax[1], data=data, orient='h')

    plt.show()
    plt.close()

if __name__ == '__main__':
    setup()
    show_lifetimes()
