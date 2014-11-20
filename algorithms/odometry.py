import math
from common.entities import SampledDistribution
from utils.probability_utils import sample_normal, get_random_element, calculate_moments, sample_multivariate_normal
import numpy as np


class Odometry:

    mul_factor = 25

    def __init__(self, a, points, landmarks):
        self.a = a
        self.points = points
        self.landmarks = landmarks

    def sample(self, number_of_samples, sensor=None):
        x0 = self.points[0][0]
        y0 = self.points[0][1]

        example_path = [(x0, y0, 0, 0)]
        sense_lines = list()

        # distributions for all time steps.
        result_distributions = [SampledDistribution(i) for i in xrange(len(self.points))]
        result_distributions[0].points.append((x0, y0, 0))

        prev_theta = 0

        for i in xrange(1, len(self.points)):
            point = self.points[i]
            if i < len(self.points) - 1:
                current_theta = math.atan2(self.points[i+1][1]-self.points[i][1], self.points[i+1][0]-self.points[i][0])

            for random_sample in xrange(number_of_samples):
                random_element = get_random_element(result_distributions[i-1].points)
                result_distributions[i].points.extend(self.eval_sample(1, self.points[i-1], point,
                                                                       random_element, current_theta, prev_theta))

            result_distributions[i].calculate_moments()
            random_point = sample_multivariate_normal(result_distributions[i].mu, result_distributions[i].sigma)[0]

            example_path.append(random_point)

            if sensor is not None:
                sensed_landmarks = sensor.sense_landmarks(random_point[0], random_point[1], random_point[2])

                if len(sensed_landmarks) > 0:
                    for sensed_landmark in sensed_landmarks:
                        sense_lines.append((random_point[0], random_point[1], sensed_landmark[0], sensed_landmark[1]))

                    result_distributions[i].points = sensor.ekf(random_point, sensed_landmarks,
                                                                np.array([point[0], point[1], random_point[2]]),
                                                                result_distributions[i].sigma,
                                                                self.mul_factor*number_of_samples, i)
            prev_theta = current_theta

        return result_distributions, example_path, sense_lines

    def eval_sample(self, number_of_samples, odometry_prev, odometry_current, current, current_theta, next_theta):
        list_of_results = list()

        for i in xrange(number_of_samples):
            list_of_results.append(self.sample_point(odometry_prev, odometry_current, current, current_theta, next_theta))

        return list_of_results

    def sample_point(self, odometry_prev, odometry_current, current, current_theta, prev_theta):
        d_x = odometry_current[0] - odometry_prev[0]
        d_y = odometry_current[1] - odometry_prev[1]

        rot1 = math.atan2(d_y, d_x) - prev_theta
        translation = math.sqrt(d_x**2 + d_y**2)
        rot2 = current_theta - prev_theta - rot1

        rot1_estimate = rot1 - sample_normal(self.a[0] * rot1 + self.a[1] * translation)
        transform_estimate = translation - sample_normal(self.a[2] * translation + self.a[3] * (rot1+rot2))
        rot2_estimate = rot2 - sample_normal(self.a[0] * rot2 + self.a[1] * translation)

        x_estimate = current[0] + transform_estimate * math.cos(current[2] + rot1_estimate)
        y_estimate = current[1] + transform_estimate * math.sin(current[2] + rot1_estimate)
        theta_estimate = current[2] + rot1_estimate + rot2_estimate

        return x_estimate, y_estimate, theta_estimate