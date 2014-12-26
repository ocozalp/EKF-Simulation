import numpy as np


def get_first_eigen_val(covariance_matrix):
    vals, vecs = np.linalg.eigh(covariance_matrix)
    vals = [v for v in vals if v > 1e-10]
    vals.sort()

    if len(vals) == 0:
        return -1, 0

    return vals[-1], len(vals)