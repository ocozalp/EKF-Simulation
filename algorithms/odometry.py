import math
from common.entities import SampledDistribution
from utils.probability_utils import sample_normal, get_random_element, calculate_moments, sample_multivariate_normal
from utils.linalg_utils import get_first_eigen_val
import numpy as np
from multirobot import update_robot_position_estimates


class Odometry:

    mul_factor = 25

    def __init__(self, a, points, landmarks):
        self.a = a
        self.points = points
        self.landmarks = landmarks

    def sample(self, number_of_samples, sensor=None, communication=None):
        example_paths = dict()
        sense_lines = dict()
        result_distributions = dict()
        robot_sense_lines = list()

        prev_theta_values = dict()

        for i, robot_points in self.points:
            x0 = robot_points[0][0]
            y0 = robot_points[0][1]
            example_paths[i] = [(x0, y0, 0, 0)]
            sense_lines[i] = list()

            # distributions for all time steps.
            result_distributions[i] = [SampledDistribution(j) for j in xrange(len(robot_points))]
            result_distributions[i][0].points.append((x0, y0, 0))

            prev_theta_values[i] = 0

        max_t_index = max([len(robot_points) for i, robot_points in self.points])

        for i in xrange(1, max_t_index):
            last_positions = dict()

            for j, robot_points in self.points:
                if i >= len(robot_points):
                    last_positions[j] = (result_distributions[j][-1], example_paths[j][-1])
                    continue

                point = robot_points[i]

                if i < len(robot_points) - 1:
                    current_theta = math.atan2(robot_points[i+1][1]-robot_points[i][1],
                                               robot_points[i+1][0]-robot_points[i][0])
                else:
                    current_theta = 0

                for random_sample in xrange(number_of_samples):
                    random_element = get_random_element(result_distributions[j][i-1].points)
                    result_distributions[j][i].points.extend(self.eval_sample(1, robot_points[i-1], point,
                                                                              random_element, current_theta,
                                                                              prev_theta_values[j]))

                result_distributions[j][i].calculate_moments()
                random_point = sample_multivariate_normal(result_distributions[j][i].mu,
                                                          result_distributions[j][i].sigma)[0]

                example_paths[j].append(random_point)

                if sensor is not None:
                    sensed_landmarks = sensor.sense_landmarks(random_point[0], random_point[1],
                                                              random_point[2], self.landmarks)
                    if len(sensed_landmarks) > 0:
                        for sensed_landmark in sensed_landmarks:
                            sense_lines[j].append((random_point[0], random_point[1],
                                                   sensed_landmark[0], sensed_landmark[1]))

                            result_distributions[j][i].points = sensor.ekf(random_point, sensed_landmarks,
                                                                           np.array([point[0], point[1],
                                                                                     random_point[2]]),
                                                                           result_distributions[j][i].sigma,
                                                                           self.mul_factor*number_of_samples, i)
                            result_distributions[j][i].calculate_moments()

                prev_theta_values[j] = current_theta
                last_positions[j] = (result_distributions[j][i], example_paths[j][-1])

            if communication:
                self.sense_robots(last_positions, robot_sense_lines, number_of_samples, communication)

        return result_distributions, example_paths, sense_lines, robot_sense_lines

    def sense_robots(self, last_positions, robot_sense_lines, number_of_samples, communication):
        for i in last_positions:
            for j in last_positions:
                if j > i:
                    p1 = last_positions[i][1]
                    p2 = last_positions[j][1]

                    if math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) <= communication.comm_distance:
                        robot_sense_lines.append((p1[0], p1[1], p2[0], p2[1]))
                        e1, ec1 = get_first_eigen_val(last_positions[i][0].sigma)
                        e2, ec2 = get_first_eigen_val(last_positions[j][0].sigma)

                        if max(e1, e2) < 1e-10 or max(ec1, ec2) < 3:
                            continue

                        s1, s2 = update_robot_position_estimates(last_positions[i][0], last_positions[j][0])

                        if not communication.one_way_enabled or e1 >= e2:
                            last_positions[i][0].points = sample_multivariate_normal(last_positions[i][0].mu, s1,
                                                                                     self.mul_factor*number_of_samples)
                            last_positions[i][0].calculate_moments()

                        if not communication.one_way_enabled or e2 >= e1:
                            last_positions[j][0].points = sample_multivariate_normal(last_positions[j][0].mu, s2,
                                                                                     self.mul_factor*number_of_samples)
                            last_positions[j][0].calculate_moments()

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