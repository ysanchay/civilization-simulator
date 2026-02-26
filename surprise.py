import math

def surprise(p):
    return -math.log(p) if p > 0 else 5.0
