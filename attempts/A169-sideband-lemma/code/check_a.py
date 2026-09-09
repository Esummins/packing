"""A169 check A: (1) the widened-box counterexample to threshold 1; (2) Lemma A' (centres of interior-disjoint unit
squares have l_inf distance >= 1/sqrt2) sampled; (3) the theta=0, delta=0.1 second meeter (refutes atlas d*(0)=0.18
as a continuous threshold); (4) distinct-cells statement sampled."""
import math, random, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geo169 import *
out = {}
# (1) widened counterexample: two 45-degree diamonds, both centres > 1 in x and y, both meet the open widened box
c = 1 + W0
D1 = verts(1.01, 1.7226, math.pi / 4); D2 = verts(1.7226, 1.01, math.pi / 4)
out['widened_cex'] = dict(gap=sat_gap(D1, D2), meet1=meets_open_box(D1, c), meet2=meets_open_box(D2, c),
                          quad=in_quadrant(D1) and in_quadrant(D2), meet1_unit=meets_open_box(D1, 1.0))
# tighten: the largest eps with centres (1+eps, c+1/sqrt2-eps') ... report the exact algebra elsewhere
# (2) sampled l_inf bound
random.seed(169); worst = 9.0; N = 200000
for _ in range(N):
    a = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, math.pi / 2))
    b = (random.uniform(0, 3), random.uniform(0, 3), random.uniform(0, math.pi / 2))
    if sat_gap(verts(*a), verts(*b)) >= 0:
        worst = min(worst, max(abs(a[0] - b[0]), abs(a[1] - b[1])))
out['linf_min_sampled'] = worst; out['linf_bound'] = 1 / math.sqrt(2)
# (3) theta = 0, delta = 0.1: explicit second meeter
Q1 = verts(0.6, 0.5, 0.0)
phi = math.asin(0.05); v = (0.05, 1.0001 - 0.05 * math.tan(phi))
cx = v[0] + (math.cos(phi) - math.sin(phi)) / 2; cy = v[1] + (math.sin(phi) + math.cos(phi)) / 2
Q2 = verts(cx, cy, phi)
out['theta0_delta01'] = dict(centre=(cx, cy), tilt_deg=math.degrees(phi), gap=sat_gap(Q1, Q2),
                             meets=meets_open_box(Q2, 1.0), quad=in_quadrant(Q2), depth=1 - v[1])
# (4) distinct cells, sampled over pairs meeting the open box (c = 1 and c = 1+w): count same-cell disjoint pairs
def cell(p, c):
    return (p[0] < c, p[1] < c)
for cc, name in ((1.0, 'unit'), (1 + W0, 'widened')):
    same = 0; pairs = 0; tries = 0
    while pairs < 20000 and tries < 3_000_000:
        tries += 1
        a = (random.uniform(0.5, 1.75), random.uniform(0.5, 1.75), random.uniform(0, math.pi / 2))
        A = verts(*a)
        if not in_quadrant(A) or not meets_open_box(A, cc):
            continue
        b = (random.uniform(0.5, 1.75), random.uniform(0.5, 1.75), random.uniform(0, math.pi / 2))
        B = verts(*b)
        if not in_quadrant(B) or not meets_open_box(B, cc) or sat_gap(A, B) < 0:
            continue
        pairs += 1
        if cell(a, cc) == cell(b, cc):
            same += 1
    out['cells_' + name] = dict(disjoint_pairs=pairs, same_cell=same, tries=tries)
json.dump(out, open(os.path.join(os.path.dirname(__file__), '..', 'results', 'check_a.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
