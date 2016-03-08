import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


def poisson_vs_exponential():
    sns.set_context("poster")
    for l in [1./7]:
        s = np.random.exponential(scale=l, size=500)
        print(s)
        sns.kdeplot(s, label='Arrival (Exponential lambda=%.0f)' % l)

    for s in [1./15]:
        expo = np.random.exponential(scale=s, size=500)
        sns.kdeplot(expo, label='Service (Exponential scale=%.0f)' % s)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    poisson_vs_exponential()
