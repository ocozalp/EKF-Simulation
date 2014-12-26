import numpy as np


class MultirobotCommunication:

    def __init__(self, one_way_enabled, comm_distance):
        self.one_way_enabled = one_way_enabled
        self.comm_distance = comm_distance


def update_robot_position_estimates(distribution1, distribution2):
    h12 = np.array([[1, 0, distribution1.mu[1] - distribution2.mu[1]],
                    [0, 1, distribution2.mu[0] - distribution1.mu[0]],
                    [0, 0, 1]])
    h12 = np.asmatrix(h12)

    s12 = h12 * distribution1.sigma * h12.T + distribution2.sigma

    s12_inv = np.linalg.inv(s12)
    sigma1 = distribution1.sigma - distribution1.sigma * h12.T * s12_inv * h12 * distribution1.sigma
    sigma2 = distribution2.sigma - distribution2.sigma * s12_inv * distribution2.sigma

    return sigma1, sigma2