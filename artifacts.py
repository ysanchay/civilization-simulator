class Artifact:
    """
    Knowledge-only structure.
    Emits patterns but gives no reward.
    """

    def __init__(self, kind):
        self.kind = kind
        self.state = 0

    def step(self, world_time):
        if self.kind == "counter":
            self.state = (self.state + 1) % 3

        elif self.kind == "cycle":
            self.state = (self.state + 1) % 4

        elif self.kind == "conditional":
            # depends on world time phase
            self.state = 1 if world_time % 2 == 0 else 0

    def observe(self):
        """
        Return symbolic observation only.
        """
        return (self.kind, self.state)
