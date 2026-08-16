import numpy as np
from pack11 import N, pack

def start_strip(rng, theta_deg=None, s0=None, jitter=0.05):
    """5 squares at angle theta in a strip along direction theta through (near) the centre;
    6 uprights placed in the two off-diagonal corner regions."""
    if s0 is None: s0 = rng.uniform(3.9, 4.05)
    if theta_deg is None: theta_deg = rng.uniform(30, 50)
    th0 = np.radians(theta_deg)
    u = np.array([np.cos(th0), np.sin(th0)]); v = np.array([-np.sin(th0), np.cos(th0)])
    ctr = np.array([s0/2, s0/2]) + rng.normal(0, 0.1, 2)
    spacing = rng.uniform(1.0, 1.08)
    c = np.zeros((N, 2)); th = np.zeros(N)
    for m in range(5):
        off = (m - 2) * spacing
        c[m] = ctr + off * u + ((-1)**m) * rng.uniform(0.0, 0.05) * v
        th[m] = th0
    # uprights: 3 in top-left region, 3 in bottom-right region; choose layouts
    layouts_tl = [[(0.5, s0-0.5), (1.5, s0-0.5), (0.5, s0-1.5)],
                  [(0.5, s0-0.5), (0.5, s0-1.5), (0.5, s0-2.5)],
                  [(0.5, s0-0.5), (1.5, s0-0.5), (2.5, s0-0.5)],
                  [(0.5, s0-0.5), (1.5, s0-0.5), (0.5, s0-1.5)]]
    layouts_br = [[(s0-0.5, 0.5), (s0-0.5, 1.5), (s0-1.5, 0.5)],
                  [(s0-0.5, 0.5), (s0-1.5, 0.5), (s0-2.5, 0.5)],
                  [(s0-0.5, 0.5), (s0-0.5, 1.5), (s0-0.5, 2.5)],
                  [(s0-0.5, 0.5), (s0-0.5, 1.5), (s0-1.5, 0.5)]]
    ltl = layouts_tl[rng.integers(len(layouts_tl))]; lbr = layouts_br[rng.integers(len(layouts_br))]
    for m in range(3):
        c[5+m] = np.array(ltl[m]) + rng.normal(0, jitter, 2)
        c[8+m] = np.array(lbr[m]) + rng.normal(0, jitter, 2)
    # sometimes 4+2 split
    if rng.random() < 0.3:
        c[8+2] = np.array([2.5 if rng.random()<0.5 else 1.5, s0-1.5]) + rng.normal(0, jitter, 2)
    if rng.random() < 0.5:   # mirror across the anti-diagonal: swap x<->y and theta -> 90-theta
        c = c[:, ::-1].copy(); th = np.pi/2 - th
    return pack(c, th, s0)
