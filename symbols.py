class Symbol:
    """
    A symbol represents a repeated pattern with survival meaning.
    """
    def __init__(self, pattern):
        self.pattern = pattern
        self.value = 0.0
        self.count = 0

    def reinforce(self, reward):
        self.count += 1
        self.value = self.value * 0.9 + reward * 0.1
