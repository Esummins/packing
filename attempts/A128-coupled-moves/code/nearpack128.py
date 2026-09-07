"""nearpack128.py -- near-packings for the converged-alive k0 cells whose LP support is FRACTIONAL and has no
A107 shadow (l1_124, l1_148, l1_158; A115 t5 LP records): A107's recipe in miniature -- take the conditioned
square plus a maximal pairwise-disjoint set of support atoms (mass-descending), then minimise the side with all
eleven squares free (penalty continuation, then SLSQP on the SAT rows).  The landing is a near-packing at its own
side s* (worst gap reported); it is the closest thing to the cell's residue the LP support defines.
Writes results/nearpack128.json.  Pure geometry, one process."""
import os, sys, json, math
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); A128 = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(A128))
sys.path.insert(0, HERE)
import coupled128 as cm

CELLS = {'l1_124': 'node_124', 'l1_148': 'node_148', 'l1_158': 'node_158'}
rng = np.random.default_rng(1128)


def load(nid):
    d = json.load(open(os.path.join(ROOT, 'attempts', 'A115-k0-corner-rows', 'results', 'nodes', nid + '.t5.lp.json')))
    s0 = float(d['s'])
    atoms = sorted(d['packing'], key=lambda q: -q['y'])
    b = d['hyp']['boxes'][0]
    cond = (0.5 * (b['x0'] + b['x1']), 0.5 * (b['y0'] + b['y1']), math.radians(0.5 * (b['th0'] + b['th1'])))
    return s0, atoms, cond


def independent_set(s0, atoms, cond):
    chosen = [cond]
    V = [cm.verts(*cond)]
    for q in atoms:
        p = (q['cx'], q['cy'], q['theta']); P = cm.verts(*p)
        if all(cm.sep(P, U) >= -0.45 for U in V) and cm.wall_gap(P, s0) >= -1e-6:
            chosen.append(p); V.append(P)
        if len(chosen) == 11:
            break
    return chosen


def polish(poses, s0):
    n = len(poses)
    x0 = np.array([c for p in poses for c in p] + [s0])

    def unpack(x):
        return [(x[3 * i], x[3 * i + 1], x[3 * i + 2]) for i in range(n)], x[-1]

    def cons(x):
        P, s = unpack(x); V = [cm.verts(*p) for p in P]
        out = [cm.sep(V[i], V[j]) for i in range(n) for j in range(i + 1, n)]
        out += [cm.wall_gap(v, s) for v in V]
        return np.array(out)

    # penalty continuation
    x = x0.copy()
    for mu in (30.0, 300.0):
        f = lambda x: x[-1] + mu * np.sum(np.minimum(cons(x), 0.0) ** 2)
        x = minimize(f, x, method='L-BFGS-B', options={'maxiter': 400}).x
    r = minimize(lambda x: x[-1], x, method='SLSQP', constraints=[{'type': 'ineq', 'fun': cons}],
                 options={'maxiter': 1500, 'ftol': 1e-14})
    x = r.x
    P, s = unpack(x)
    return P, float(s), float(cons(x).min())


out = {}
for cell, nid in CELLS.items():
    s0, atoms, cond = load(nid)
    best = None
    for trial in range(3):
        at = atoms if trial == 0 else sorted(atoms, key=lambda q: -(q['y'] + 0.3 * rng.random()))
        chosen = independent_set(s0, at, cond)
        print(cell, 'trial', trial, 'chosen', len(chosen), flush=True)
        if len(chosen) < 11:
            continue
        P, s, wg = polish(chosen, s0)
        print(cell, 'trial', trial, 'n', len(chosen), 'side %.6f worst gap %.2e' % (s, wg), flush=True)
        if wg >= -1e-6 and (best is None or s < best[1]):
            best = (P, s, wg)
    if best is None:
        out[cell] = {'status': 'no packing found'}
        continue
    P, s, wg = best
    out[cell] = {'node': nid, 'side': s, 'worst_gap': wg, 'poses': [[float(v) for v in p] for p in P], 'lp_side': s0,
                 'note': 'near-packing of the LP support (A115 t5 record), all eleven squares polished free; side s* = %.6f, worst gap %.1e' % (s, wg)}
json.dump(out, open(os.path.join(A128, 'results', 'nearpack128.json'), 'w'), indent=1)
print(json.dumps({k: (v.get('side'), v.get('worst_gap')) for k, v in out.items()}))
