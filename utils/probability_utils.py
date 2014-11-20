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


def sample_multivariate_normal(mu, sigma, cnt=1):
    return np.random.multivariate_normal(mu, sigma, cnt)


def get_random_element(elm_list):
    length_of_list = len(elm_list)
    return elm_list[int(sample_uniform() * length_of_list)]


def calculate_moments(points):
    point_array = np.array([[point[0], point[1], point[2]] for point in points])
    mu = np.mean(point_array, axis=0)
    sigma = np.zeros((3, 3))

    for point in point_array:
        for i in xrange(3):
            for j in xrange(3):
                sigma[i, j] += (point[i] - mu[i])*(point[j] - mu[j])

    for i in xrange(3):
        for j in xrange(3):
            sigma[i, j] /= len(points) - 1
    return mu.T, sigma