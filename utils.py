import math
import numpy as np

def clamp(val, minv, maxv):
    return max(minv, min(val, maxv))

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# Çeşitlilik skoru: hız ve boyut varyanslarının toplamı

def diversity_score(blobs):
    if not blobs:
        return 0
    speeds = np.array([b.speed for b in blobs])
    sizes = np.array([b.size for b in blobs])
    speed_var = np.var(speeds)
    size_var = np.var(sizes)
    return speed_var + size_var 