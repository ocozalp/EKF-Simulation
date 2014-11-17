import math
from utils.probability_utils import sample_normal, get_random_element, calculate_moments, sample_multivariate_normal
import numpy as np


class Odometry:

    def __init__(self, a, points, landmarks):
        self.a = a
        self.points = points
        self.landmarks = landmarks

    def sample(self, number_of_samples, sensor=None):
        all_points = list()
        x0 = self.points[0][0]
        y0 = self.points[0][1]

        prev_points = list()
        prev_points.append((x0, y0, 0, 0))

        all_points.extend(prev_points)

        mul_factor = 10

        example_path = list()
        example_path.append((x0, y0, 0, 0))

        sense_lines = list()

        for sample_index in xrange(1, len(self.points)):
            point = self.points[sample_index]
            temp_points = list()

            for random_sample in xrange(mul_factor):
                random_element = get_random_element(prev_points)

                d_y = float(point[1] - random_element[1])
                d_x = float(point[0] - random_element[0])
                theta = math.atan2(d_y, d_x)

                temp_points.extend(self.eval_sample(number_of_samples, random_element[0], random_element[1], point[0],
                                                    point[1], random_element[2], theta, sample_index))

            mu, sigma = calculate_moments(temp_points)
            random_point = sample_multivariate_normal(mu, sigma, 1)[0]

            example_path.append(random_point)
            if sensor is not None:
                sensed_landmarks = sensor.sense_landmarks(random_point[0], random_point[1], random_point[2])

                if len(sensed_landmarks) > 0:
                    for sensed_landmark in sensed_landmarks:
                        sense_lines.append((random_point[0], random_point[1], sensed_landmark[0], sensed_landmark[1]))

                    temp_points = sensor.ekf(random_point, sensed_landmarks,
                                             np.array([point[0], point[1], random_point[2]]), sigma,
                                             mul_factor*number_of_samples, sample_index)

            prev_points = temp_points
            all_points.extend(prev_points)

        return all_points, example_path, sense_lines

    def eval_sample(self, number_of_samples, x0, y0, x1, y1, theta0, theta1, sample_index):
        list_of_results = list()

        for i in xrange(number_of_samples):
            list_of_results.append(self.sample_point(x0, y0, x1, y1, theta0, theta1, sample_index))

        return list_of_results

    def sample_point(self, x0, y0, x1, y1, theta0, theta1, sample_index):
        d_x = x1 - x0
        d_y = y1 - y0
        rot1 = math.atan2(d_y, d_x) - theta0
        translation = math.sqrt(d_x**2 + d_y**2)
        rot2 = theta1 - theta0 - rot1

        rot1_estimate = rot1 - sample_normal(self.a[0] * rot1 + self.a[1] * translation)
        transform_estimate = translation - sample_normal(self.a[2] * translation + self.a[3] * (rot1+rot2))
        rot2_estimate = rot2 - sample_normal(self.a[0] * rot2 + self.a[1] * translation)

        x_estimate = x0 + transform_estimate * math.cos(theta0 + rot1_estimate)
        y_estimate = y0 + transform_estimate * math.sin(theta0 + rot1_estimate)
        theta_estimate = theta0 + rot1_estimate + rot2_estimate

        return x_estimate, y_estimate, theta_estimate, sample_index