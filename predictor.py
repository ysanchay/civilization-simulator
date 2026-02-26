from collections import defaultdict

class Predictor:
    def __init__(self):
        self.counts = defaultdict(int)
        self.total = 0

    def update(self, obs):
        self.counts[obs] += 1
        self.total += 1
