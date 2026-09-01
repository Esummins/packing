"""
A53 canary: Trump's own packing is feasible in the trump5 residual stratum at s0.

Embedding: his packing at side s_T anchored at the origin, with the BR and TR pinned
squares moved to the s0 slots (outward by s0 - s_T = 4.1e-7; they only move AWAY from
the other ten squares, so disjointness is preserved -- checked exactly below in floats
with margin reporting). The six free squares (the epsilon-off upright + five tilted)
are then admissible placements of the residual region: each is disjoint from all five
pins. Consequently the TRUE residual guard LP value satisfies tau* >= 6 (six disjoint
placements each carry mass >= 1), i.e. the trump5 stratum is UNKILLABLE by the guard LP
-- the canary is that the LP must NOT certify a kill here.
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_skel import hyp_from_slots, S0F

trump = json.load(open(os.path.join(HERE, "..", "..", "A03-upper-reconstruct", "trump11_float.json")))
X = trump["X"]
pins = [(0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (S0F - 0.5, 0.5), (S0F - 0.5, S0F - 0.5)]
free = [X[i] for i in (4, 6, 7, 8, 9, 10)]

def sat_gap(c1, t1, c2, t2):
    """min over the 4 SAT axes of (separation - required); >= 0 iff interior-disjoint."""
    best = -1e9
    for (cc, tt, oc, ot) in ((c1, t1, c2, t2), (c2, t2, c1, t1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            d = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = (abs(ax[0] * math.cos(ot) + ax[1] * math.sin(ot)) +
                 abs(-ax[0] * math.sin(ot) + ax[1] * math.cos(ot)))
            best = max(best, d - 0.5 - 0.5 * g)
    return best

hyp = hyp_from_slots(pins)
print("free square | admissible | min SAT gap to pins | kept by LP row filter")
ok_all = True
for (cx, cy, th) in free:
    w = (math.cos(th) + math.sin(th)) / 2
    adm = w - 1e-12 <= cx <= S0F - w + 1e-12 and w - 1e-12 <= cy <= S0F - w + 1e-12
    g = min(sat_gap((cx, cy), th, p, 0.0) for p in pins)
    kept = hyp.ok(cx, cy, th)
    ok_all &= adm and g >= -1e-9 and kept
    print(f"({cx:.4f},{cy:.4f},{math.degrees(th):6.2f}deg) | {adm} | {g:+.6e} | {kept}")
# pairwise disjointness of the six free squares among themselves
gmin = 1e9
for i in range(6):
    for j in range(i + 1, 6):
        gmin = min(gmin, sat_gap(free[i][:2], free[i][2], free[j][:2], free[j][2]))
print(f"min pairwise SAT gap among the six free squares: {gmin:+.6e}")
print("FEASIBLE (=> true residual tau* >= 6):", ok_all and gmin >= -1e-9)
