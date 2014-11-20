from utils.probability_utils import calculate_moments


class SampledDistribution:
    def __init__(self, distribution_id):
        self.distribution_id = distribution_id
        self.points = list()

    def calculate_moments(self):
        self.mu, self.sigma = calculate_moments(self.points)