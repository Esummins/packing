"""A21: build hypothesis jsons for the structure nodes at s = 3.88 (= 97/25).
All nodes are pure NO-family nodes, budget 11.
Zones = A13 make_zones(s, 0.6): a=0.5, b=s-0.5=3.38, corner cw=0.6 (c0=1.1, c1=2.78).
Theta families: zone = whole centre domain [0.5, 3.38]^2, thetas = complement of the tested angle box.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import NoFam, Hyp
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "A13-case-lp-bnb"))
from bnb import make_zones, zone_family

S = 3.88
Z = make_zones(S, 0.6)
DOM = (0.5, S - 0.5, 0.5, S - 0.5)

def th_fam(ths):
    return NoFam(DOM[0], DOM[1], DOM[2], DOM[3], ths)

hyps = {
    # task 1
    "corners4": Hyp([], [zone_family(n, Z[n]) for n in ("corner0", "corner1", "corner2", "corner3")]),
    "corner0":  Hyp([], [zone_family("corner0", Z["corner0"])]),
    # task 2
    "sides4":   Hyp([], [zone_family(n, Z[n]) for n in ("side0", "side1", "side2", "side3")]),
    "side0":    Hyp([], [zone_family("side0", Z["side0"])]),
    # task 3 (family = complement of the angle box Theta_B; theorem = some square has theta in the family)
    # (a) Theta_B = [10,35] u [55,80]  (no square near upright or near diagonal)
    "th_a":     Hyp([], [th_fam([(0.0, 10.0), (35.0, 55.0), (80.0, 90.0)])]),
    # (b) Theta_B = [0,10] u [80,90]  (all near-upright)
    "th_b":     Hyp([], [th_fam([(10.0, 80.0)])]),
    # (c) Theta_B = [0,5] u [43,47] u [85,90]  (near-upright / near-diagonal with Trump's theta*=40.18 excluded)
    "th_c":     Hyp([], [th_fam([(5.0, 43.0), (47.0, 85.0)])]),
    # (c') the PI's literal window [0,5] u [40,50] u [85,90] -- contains Trump (0, 40.18): expected ALIVE
    "th_c_lit": Hyp([], [th_fam([(5.0, 40.0), (50.0, 85.0)])]),
}
for k, h in hyps.items():
    p = os.path.join(HERE, "results", f"hyp_{k}.json")
    json.dump(h.to_json(), open(p, "w"))
    print(k, "D4" if h.is_symmetric_D4(S) else "C1", h.describe())
