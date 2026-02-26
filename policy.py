OBSERVE = 0
MOVE = 1

class Policy:
    def decide(self, intent, energy):
        if energy < 8:
            return OBSERVE
        return MOVE if intent == "MOVE" else OBSERVE
