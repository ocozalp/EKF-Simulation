import math
import numpy as np
import numpy.linalg as linalg
from utils.geom_utils import convert_degree_to_radian
from utils.probability_utils import sample_multivariate_normal


class LaserSensor:
    def __init__(self, r, sensor_theta, distance_error, theta_error, signature_error, landmarks):
        self.r = r
        self.sensor_theta = convert_degree_to_radian(sensor_theta)
        self.distance_error = distance_error
        self.theta_error = theta_error
        self.signature_error = signature_error
        self.landmarks = landmarks

    def sense_landmarks(self, x, y, theta):
        result = list()

        for landmark in self.landmarks:
            dist = math.sqrt((landmark[1] - y) ** 2 + (landmark[0] - x) ** 2)
            if dist > self.r:
                continue

            landmark_theta = math.atan2(landmark[1] - y, landmark[0] - x)
            if landmark_theta < 0:
                landmark_theta += math.pi * 2

            lower = theta - (self.sensor_theta / 2.0)
            if lower < 0:
                lower += math.pi * 2

            upper = theta + (self.sensor_theta / 2.0)
            if upper < 0:
                upper += math.pi * 2

            if lower <= landmark_theta <= upper:
                result.append(landmark)
            elif lower > upper and (upper < lower <= landmark_theta or landmark_theta <= upper < lower):
                result.append(landmark)

        return result

    def ekf(self, current_point, sensed_landmarks, mu, sigma, number_of_samples, sample_index):
        #added 0.0001, otherwise Q_t can not be inverted.
        Q_t = np.matrix([[0.0001 + self.distance_error, 0, 0], [0, 0.0001 + self.theta_error, 0], [0, 0, 0.0001 + self.signature_error]])

        real_z_vectors = list()
        z_vectors = list()
        h_matrices = list()
        kalman_gains = list()

        for sensed_landmark in sensed_landmarks:
            d_x = sensed_landmark[0] - current_point[0]
            d_y = sensed_landmark[1] - current_point[1]
            q = d_x * d_x + d_y * d_y
            sqrt_q = math.sqrt(q)

            real_z_vector = np.array([sqrt_q, math.atan2(d_y, d_x) - current_point[2], sensed_landmark[2]]).T
            real_z_vectors.append(real_z_vector)

            h = np.matrix([[d_x/sqrt_q, -d_y/sqrt_q, 0], [d_y/q, d_x/q, -1.0/q], [0, 0, 0]])
            h_matrices.append(h)

            kalman_gain = sigma * h.T * linalg.inv(h * sigma * h.T + Q_t)
            kalman_gains.append(kalman_gain)

            d_x = sensed_landmark[0] - mu[0]
            d_y = sensed_landmark[1] - mu[1]
            q = d_x * d_x + d_y * d_y
            sqrt_q = math.sqrt(q)

            z_vector = np.array([sqrt_q, math.atan2(d_y, d_x) - mu[2], sensed_landmark[2]]).T
            z_vectors.append(z_vector)

        for i in xrange(len(sensed_landmarks)):
            mu = mu + np.matrix(kalman_gains[i] * np.matrix(z_vectors[i].T - real_z_vectors[i].T).T).A1

        sub_total = kalman_gains[0] * h_matrices[0]
        for i in xrange(1, len(sensed_landmarks)):
            sub_total += kalman_gains[i] * h_matrices[i]

        sub_total = np.identity(3) - sub_total
        sigma = sub_total * sigma

        result = list()
        random_results = sample_multivariate_normal(mu, sigma, number_of_samples)
        for random_result in random_results:
            result.append((random_result[0], random_result[1], random_result[2], sample_index))

        return result