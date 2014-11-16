import math
from utils.geom_utils import convert_degree_to_radian, convert_radian_to_degree


class LaserSensor:
    def __init__(self, r, sensor_theta, landmarks):
        self.r = r
        self.sensor_theta = convert_degree_to_radian(sensor_theta)
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