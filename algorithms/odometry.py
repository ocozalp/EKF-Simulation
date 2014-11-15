import math
from utils.probability_utils import sample_normal, eval_normal, sample_uniform
import numpy as np


class Odometry:

    def __init__(self, a, points):
        self.a = a
        self.points = points

    def direct(self, resolution=11):
        result = list()
        x0_rect, y0_rect = np.mgrid[self.points[0][0]-0.2:self.points[0][0]+0.2:resolution*1j,
                                    self.points[0][1]-0.2:self.points[0][1]+0.2:resolution*1j]
        px0_rect = np.array([0.0] * (resolution ** 2))
        px0_rect = px0_rect.reshape(x0_rect.shape)
        px0_rect[resolution//2][resolution//2] = 1

        theta0_probs = [0.0] * 360
        theta0_probs[0] = 1.0

        result.append((x0_rect, y0_rect, px0_rect, theta0_probs, self.points[0], 0.0))

        for i in xrange(1, len(self.points)):
            prev_result = result[i-1]
            odometry_x = prev_result[4][0]
            odometry_y = prev_result[4][2]
            odometry_theta = prev_result[5]

            print odometry_x, odometry_y, odometry_theta

            x_rect, y_rect = np.mgrid[self.points[i][0]-0.2:self.points[i][0]+0.2:resolution*1j,
                                      self.points[i][1]-0.2:self.points[i][1]+0.2:resolution*1j]
            px_rect = np.array([0.0] * (resolution ** 2)).reshape(x_rect.shape)

            theta_probs = [0.0] * 360

            for angle in xrange(360):
                probability = self.eval_direct(self.points[i][0], self.points[i][1],
                                               self.points[i-1][0], self.points[i-1][1],
                                               self.points[i][0], self.points[i][1],
                                               odometry_x, odometry_y, odometry_theta,
                                               (angle*math.pi)/180.0, 0, 0)

            result.append((x_rect, y_rect, px_rect, theta_probs, self.points[i]))

        return result

    def get_sample_point(self, point_result, resolution):
        flat_px = point_result[2].flatten()

        for i in xrange(1, len(flat_px)):
            flat_px[i] += flat_px[i - 1]

        r = sample_uniform()
        for i in xrange(len(flat_px)):
            if r < flat_px[i]:
                row = i // resolution
                col = i % resolution

                return point_result[0][row][col], point_result[1][row][col]

        raise Exception('nokta bulunurken hata alindi')

    def get_sample_theta(self, point_result):
        total = 0.0
        theta_list = point_result[3]
        r = sample_uniform()

        for i in xrange(len(theta_list)):
            total += theta_list[i]
            if total > r:
                return (i*math.pi) / 180.0

        raise Exception('theta bulunurken hata alindi')

    def eval_direct(self, x1, y1, x0, y0, odometry_x1, odometry_y1, odometry_x0, odometry_y0,
                    odometry_theta0, odometry_theta1, theta0, theta1):
        rot1 = math.atan2(odometry_y1 - odometry_y0, odometry_x1 - odometry_x0) - odometry_theta0
        trans = math.sqrt((odometry_x1 - odometry_x0) ** 2 + (odometry_y1 - odometry_y0) ** 2)
        rot2 = odometry_theta1 - odometry_theta0 - rot1

        e_rot1 = math.atan2(y1 - y0, x1 - x0) - theta0
        e_trans = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        e_rot2 = theta1 - theta0 - e_rot1

        p1 = eval_normal(rot1 - e_rot1, 0, self.a[0] * e_rot1 + self.a[1] * e_trans)
        p2 = eval_normal(trans - e_trans, 0, self.a[2] * e_trans + self.a[3] * (e_rot1 + e_rot2))
        p3 = eval_normal(rot2 - e_rot2, 0, self.a[0] * e_rot2 + self.a[1] * e_trans)

        return p1 * p2 * p3

    def sample(self, number_of_samples):
        all_points = list()
        x0 = self.points[0][0]
        y0 = self.points[0][1]

        prev_points = list()
        prev_points.append((x0, y0, 0, 0))

        sample_index = 1

        for point in self.points[1:]:
            temp_prev = list()
            for prev_point in prev_points:
                d_y = float(point[1] - prev_point[1])
                d_x = float(point[0] - prev_point[0])
                theta = math.atan2(d_y, d_x)

                single_result = self.eval_sample(number_of_samples, prev_point[0], prev_point[1], point[0], point[1],
                                                  prev_point[2], theta, sample_index)

                all_points.extend(single_result)
                temp_prev.extend(single_result)
            prev_points = temp_prev
            sample_index += 1

        return all_points

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