"""canon.py -- canonicalise a packing under the D4 symmetry of the container and sort squares.
Uprights (angle within tol of 0 mod pi/2) first, sorted by (y, x); tilted squares after, sorted by x.
Chosen image: mean tilted angle < 45 deg if possible; then minimal sum of upright centre coordinates
(uprights hug the bottom-left)."""
import math
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'code'))
from squares import normalise_angles


def transform(X, s, k, refl):
    Y = np.array(X, dtype=float)
    if refl:  # reflect in the main diagonal
        Y = np.stack([Y[:, 1], Y[:, 0], math.pi / 2 - Y[:, 2]], 1)
    for _ in range(k):  # rotate 90 deg CCW about the container centre
        Y = np.stack([s - Y[:, 1], Y[:, 0], Y[:, 2] + math.pi / 2], 1)
    return normalise_angles(Y)


def canonicalise(X, s, tol=1e-6):
    best = None
    n = len(X)
    for k in range(4):
        for refl in (0, 1):
            Y = transform(X, s, k, refl)
            up = [i for i in range(n) if min(abs(Y[i, 2]), abs(Y[i, 2] - math.pi / 2)) < tol]
            tl = [i for i in range(n) if i not in up]
            key = (float(np.mean(Y[tl, 2])) > math.pi / 4 if tl else False, round(float(np.sum(Y[up, :2])), 6))
            if best is None or key < best[0]:
                best = (key, Y, up, tl)
    _, Y, up, tl = best
    up = sorted(up, key=lambda i: (round(Y[i, 1], 3), Y[i, 0]))
    tl = sorted(tl, key=lambda i: Y[i, 0])
    Y = Y[up + tl]
    Y[:len(up), 2] = 0.0
    return Y, len(up)
