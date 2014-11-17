import math
from utils.probability_utils import sample_normal


class DeadReckoning:

    def __init__(self, a_values):
        self.a_values = a_values

    def eval_sample(self, x0, y0, number_of_samples, v, w, theta, delta_t):
        list_of_points = list()

        for i in xrange(number_of_samples):
            list_of_points.append(self.sample_point(x0, y0, v, w, theta, delta_t))

        return list_of_points

    def sample_circular(self, r, xc, yc, number_of_points, number_of_samples):
        all_points = list()
        w = (math.pi * 2) / number_of_points
        v = w * r
        theta = 0

        for i in xrange(number_of_points):
            x0 = xc + r*math.sin(theta)
            y0 = yc - r*math.cos(theta)
            single_result = self.eval_sample(x0, y0, number_of_samples, v, w, theta, 1)
            theta += w
            all_points.extend(single_result)

        return all_points

    def sample_rectangular(self, r, points, number_of_samples):
        all_points = list()
        x0 = points[0][0]
        y0 = points[0][1]

        v = 1
        for point in points[1:]:
            d_y = float(point[1] - y0)
            d_x = float(point[0] - x0)
            theta = math.atan2(d_y, d_x)

            tx = x0 + d_x / 2.0
            ty = y0 + d_y / 2.0
            tl = math.sqrt((tx-x0)*(tx-x0) + (ty-y0)*(ty-y0))
            tl2 = math.sqrt(r*r - tl-tl)

            w = math.atan2(tl, tl2) * 2.0

            single_result = self.eval_sample(x0, y0, number_of_samples, v, w, theta, 1)

            x0 = point[0]
            y0 = point[1]

            all_points.extend(single_result)

        return all_points

    def sample_point(self, x, y, v, w, theta, delta_t):
        v_prime = v + sample_normal(0, self.a_values[0] * v + self.a_values[1] * w)
        w_prime = w + sample_normal(0, self.a_values[2] * v + self.a_values[3] * w)
        err = sample_normal(0, self.a_values[4] * v + self.a_values[5] * w)

        x_prime = x - (v_prime/w_prime)*(math.sin(theta) - math.sin(theta + w_prime * delta_t))
        y_prime = y + (v_prime/w_prime)*(math.cos(theta) - math.cos(theta + w_prime * delta_t))
        theta_prime = theta + w_prime * delta_t + err * delta_t

        return x_prime, y_prime, theta_prime