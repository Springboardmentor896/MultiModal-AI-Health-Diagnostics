import math

def to_probability(score):
    prob = 1 / (1 + math.exp(-score / 10))
    return round(prob * 100, 2)
