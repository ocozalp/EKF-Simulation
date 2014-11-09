import math
from probability_utils import sample_normal


class Odometry:

    def __init__(self, a):
        self.a = a

    def eval_direct(self):
        pass

    def sample_circular(self, r, xc, yc, number_of_points, number_of_samples):
        all_points = list()
        w = (math.pi * 2) / number_of_points
        theta = 0
        x_p = xc
        y_p = yc - r

        prev_points = list()
        for i in xrange(number_of_samples):
            prev_points.append((x_p, y_p, 0))

        for i in xrange(number_of_points):
            temp_prev = list()
            for prev_point in prev_points:
                x0 = xc + r*math.sin(theta)
                y0 = yc - r*math.cos(theta)
                single_result = self.sample_point(prev_point[0], prev_point[1], x0, y0, prev_point[2], theta)
                theta += w
                all_points.append(single_result)
                temp_prev.append(single_result)
            prev_points = temp_prev

        return all_points

    def sample_rectangular(self, points, number_of_samples):
        all_points = list()
        x0 = points[0][0]
        y0 = points[0][1]

        prev_points = list()
        for i in xrange(number_of_samples):
            prev_points.append((x0, y0, 0))

        for point in points[1:]:
            temp_prev = list()
            for prev_point in prev_points:
                d_y = float(point[1] - prev_point[1])
                d_x = float(point[0] - prev_point[0])
                theta = math.atan2(d_y, d_x)

                single_result = self.sample_point(prev_point[0], prev_point[1], point[0], point[1],
                                                  prev_point[2], theta)

                all_points.append(single_result)
                temp_prev.append(single_result)
            prev_points = temp_prev

        return all_points

    def eval_sample(self, number_of_samples, x0, y0, x1, y1, theta0, theta1):
        list_of_results = list()

        for i in xrange(number_of_samples):
            list_of_results.append(self.sample_point(x0, y0, x1, y1, theta0, theta1))

        return list_of_results

    def sample_point(self, x0, y0, x1, y1, theta0, theta1):
        d_x = x1 - x0
        d_y = y1 - y0
        rot1 = math.atan2(d_y, d_x) - theta0
        transform = math.sqrt(d_x**2 + d_y**2)
        rot2 = theta1 - theta0 - rot1

        rot1_estimate = rot1 - sample_normal(self.a[0] * rot1 + self.a[1] * transform)
        transform_estimate = transform - sample_normal(self.a[2] * transform + self.a[3] * (rot1+rot2))
        rot2_estimate = rot2 - sample_normal(self.a[0] * rot2 + self.a[1] * transform)

        x_estimate = x0 + transform_estimate * math.cos(theta0 + rot1_estimate)
        y_estimate = y0 + transform_estimate * math.sin(theta0 + rot1_estimate)
        theta_estimate = theta0 + rot1_estimate + rot2_estimate

        return x_estimate, y_estimate, theta_estimate