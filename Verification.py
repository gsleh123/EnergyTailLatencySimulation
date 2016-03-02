import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


def poisson_vs_exponential():
    sns.set_context("poster")
    for l in xrange(9, 10, 3):
        poi = np.random.poisson(lam=l, size=500)
        sns.kdeplot(poi, label='Arrival (Poisson lambda=%.0f)' % l)

    for s in xrange(8, 11, 8):
        expo = np.random.exponential(scale=s, size=500)
        sns.kdeplot(expo, label='Service (Exponential scale=%.0f)' % s)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    poisson_vs_exponential()
