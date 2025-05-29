import math

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1]) 