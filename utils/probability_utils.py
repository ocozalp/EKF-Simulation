import random
import numpy as np
import math


def sample_normal(b):
    return random.gauss(0, b)


def sample_uniform():
    return random.random()


def eval_normal(x, mu, sigma):
    if sigma < 1e-6:
        if x == mu:
            return 1.0
        return 0.0

    return (1.0 / (math.sqrt(2*math.pi*sigma))) * math.e ** -(((x-mu)**2) / sigma)


def sample_bivariate_normal(mu, sigma):
    return np.random.multivariate_normal(mu, sigma)