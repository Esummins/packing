"""Side minimum vs the common tilt of the free squares, slot squares fixed (PI question 2026-09-06: what happens when
f0..f3 rotate together). Usage: python gen_pinwheel_tilt.py [result.json] — reads the slot list and free squares from a
gen_pinwheel_k7.py result and sweeps the tilt; prints a table and writes <name>_tilt.json."""
import json, math, sys, os
import numpy as np
from scipy.optimize import minimize
SHAT = 3.877083590022814
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pinwheel_k7_result.json')
d = json.load(open(src)); s0 = d['s']; F = [tuple(f) for f in d['free']]
def sat_gap(c1, t1, c2, t2):
    best = -1e9
    for (cc, tt, oc, ot) in ((c1, t1, c2, t2), (c2, t2, c1, t1)):
        co, si = math.cos(tt), math.sin(tt)
        for ax in ((co, si), (-si, co)):
            dd = abs((oc[0]-cc[0])*ax[0] + (oc[1]-cc[1])*ax[1]); g = abs(ax[0]*math.cos(ot) + ax[1]*math.sin(ot)) + abs(-ax[0]*math.sin(ot) + ax[1]*math.cos(ot))
            best = max(best, dd - 0.5 - 0.5*g)
    return best
def fixed(s):  # k7 shadow slots: BL L-shape, TL, TR, BR stacked; edit for other shadows or read d['slots'] if present
    if 'slots' in d: return [(x if x >= 0 else s + x, y if y >= 0 else s + y) for x, y in d['slots']]
    return [(0.5, 0.5), (1.5, 0.5), (0.5, 1.5), (0.5, s-0.5), (s-0.5, s-0.5), (s-0.5, 0.5), (s-0.5, 1.5)]
def run(theta, n):
    def cons(z):
        s = z[0]; P = [(z[1+2*i], z[2+2*i]) for i in range(n)]; out = []; w = (abs(math.cos(theta)) + abs(math.sin(theta)))/2
        for i in range(n):
            out += [P[i][0]-w, s-w-P[i][0], P[i][1]-w, s-w-P[i][1]]
            for j in range(i+1, n): out.append(sat_gap(P[i], theta, P[j], theta))
            for p in fixed(s): out.append(sat_gap(P[i], theta, p, 0.0))
        return np.array(out)
    best = None
    for k in range(4):
        z0 = np.array([s0+0.05] + [v for f in F[:n] for v in f[:2]])
        if k: z0[1:] += np.random.RandomState(k).uniform(-0.1, 0.1, 2*n)
        r = minimize(lambda z: z[0], z0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': cons}], bounds=[(3.5, 4.6)] + [(0, 4.6)]*(2*n), options={'maxiter': 300, 'ftol': 1e-12})
        if cons(r.x).min() >= -1e-7 and (best is None or r.x[0] < best[0]): best = (r.x[0], r.x.tolist())
    return best
out = []
for th in [36, 40, 42, 44, 45, 46, 47, 48, 48.435, 49, 50, 52, 54, 56, 60]:
    t = math.radians(th); bn = run(t, len(F)); bc = run(t, len(F)-1)
    print(f'{th:7.3f}  s*({len(F)} sq) {bn[0] if bn else float("nan"):.6f}   s*({len(F)-1} sq) {bc[0] if bc else float("nan"):.6f}')
    out.append({'tilt_deg': th, 's_all': bn[0] if bn else None, 's_core': bc[0] if bc else None})
json.dump(out, open(src.replace('.json', '_tilt.json'), 'w'), indent=1); print('s-hat', SHAT)
