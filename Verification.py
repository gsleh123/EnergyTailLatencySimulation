import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def poisson_vs_exponential():
    sns.set_context("poster")
    for l in [2.133]:
        s = np.random.lognormal(mean=165, sigma=l, size=300)
        print(s)
        sns.kdeplot(s, label='Lognormal mean=165 sigma=%.0f' % l)

    # for s in [1./15]:
    #     expo = np.random.exponential(scale=s, size=500)
    #     sns.kdeplot(expo, label='Service (Exponential scale=%.0f)' % s)

    plt.tight_layout()
    plt.show()


def explore_lognormal():
    sns.set_context("poster")
    for mean in [1.65]:
        for sigma in [.02133]:
            s = np.random.lognormal(mean=mean, sigma=sigma, size=100)
            print(min(s))
            print(np.mean(s))
            print(max(s))
            sns.kdeplot(s, label='Lognormal mean=%.1f sigma=%.3f' % (mean, sigma))

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    explore_lognormal()
