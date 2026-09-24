"""A274 route R1, numerically: on the near-flat corner theta_C, phi_X in [0, 5 deg] of the H1-H3 set, minimise each
ring inequality (U3), (U4), (U5), (U6), (U8) (ringdom271.conditions = hyp267's margins) separately under H1-H3 HARD
(ringdom271.constraints >= EPS, adv271's penalty, imported, never edited) from structured starts; the minimiser is
rationalised (tan of half-angles, Fractions) and H1-H3 re-checked EXACTLY (witness273's SAT helpers) before it is
reported.  Mode 'curve': STRIP_2's own margin -sup t_L (left272's square statement, A273's curve) at theta = phi and
at phi = 0 for 5, 2, 1, 0.5 deg.  Mode 'page': the failing configurations drawn (geometry-checked).
    python r1_274.py adv [seconds] | curve [seconds] | page -> results/r1_274_{adv,curve}.json (merged by hand into
    results/r1_274.json = {adv, curve}; page reads the merged file) + docs/residue_map/campaigns/A274-flat-corner/r1_274.svg"""
import json
import math
import os
import sys
import time
from fractions import Fraction as F

import numpy as np
from scipy.optimize import minimize

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for d in ('A271-ring-domain', 'A272-strip-jam', 'A273-disc-lemma'):
    sys.path.insert(0, os.path.join(ROOT, 'attempts', d, 'code'))
import ringdom271 as R                                                # noqa: E402
import adv271 as ADV                                                  # noqa: E402
import witness273 as W                                                # noqa: E402

RES = os.path.join(HERE, '..', 'results')
DEG = R.DEG
AMAX = 5 * DEG * (1 - 1e-9)
KEYS = ['U3', 'U4', 'U5', 'U6', 'U8']
LO = ADV.LO.copy()
HI = ADV.HI.copy()
HI[2] = HI[4] = AMAX


def w(t):
    return math.cos(t) + math.sin(t)


def clip(q):
    return np.clip(q, LO, HI)


def feasible(q):
    return bool(R.constraints(q).min() >= ADV.EPS)


def fill_A(hu, hv, th, xl, phi, side):
    """(a_x, alpha) maximising the smallest H1-H3 margin (grid + short Nelder-Mead)."""
    def m(z):
        return float(R.constraints(np.array([hu, hv, th, xl, phi, z[0], z[1], side])).min())
    best = max((m((a, al)), (a, al)) for a in np.linspace(0.05, 1.9, 18) for al in np.radians(np.linspace(0.2, 80, 12)))
    r = minimize(lambda z: -m(z), np.array(best[1]), method='Nelder-Mead', options=dict(maxfev=200, xatol=1e-8))
    z = r.x if -r.fun > best[0] else np.array(best[1])
    return np.array([hu, hv, th, xl, phi, z[0], z[1], side])


def structured_starts(rng, n):
    """angles on {0, 0.5, 2, 5 deg} and random; X_low anywhere in its H1 window below C_top; A filled."""
    out, tries = [], 0
    while len(out) < n and tries < 60 * n:
        tries += 1
        th = rng.choice([0.0, 0.5 * DEG, 2 * DEG, AMAX, rng.random() * AMAX])
        phi = rng.choice([0.0, 0.5 * DEG, 2 * DEG, AMAX, rng.random() * AMAX])
        hu, hv, side = rng.random(), 1 - 0.3 * rng.random() ** 2, 3.82 + (R.SHAT - 3.82) * rng.random()
        xl = hv + w(th) - 10 ** rng.uniform(-3.5, -0.7)                # X_low = C_top - D, D log-uniform
        if not (max(1.0, side - 1 - w(phi)) < xl <= side - w(phi)):
            continue
        C, X, A, Tu = R.squares(np.array([hu, hv, th, xl, phi, 5.0, 0.0, side]))
        if min(R.depth(X, Tu), R.Z.poly_gap(X, C)) < ADV.EPS:        # X holds C and misses it: test before A
            continue
        q = fill_A(hu, hv, th, xl, phi, side)
        if feasible(q):
            out.append(q)
    return out


def objective(key):
    base = ADV.penalised(key)

    def f(q):
        ex = np.maximum(q - HI, 0) + np.maximum(LO - q, 0)
        return base(q) + 1e4 * float(ex @ ex)
    return f


TAN_HALF_5 = F(43660942908, 10 ** 12)                              # < tan(2.5 deg) = 0.0436609429085...


def rationalise(q, den=10 ** 7):
    hu, hv, th, xl, phi, ax, al, side = q
    fr = lambda v: F(float(v)).limit_denominator(den)                 # noqa: E731
    return dict(hu=fr(hu), hv=fr(hv), tC=fr(math.tan(th / 2)), xl=fr(xl), tX=fr(math.tan(phi / 2)), ax=fr(ax),
                tA=fr(math.tan(al / 2)), side=fr(side))


def exact_check(q):
    """H1-H3 in Fractions on the rationalised configuration (SAT on edge normals); returns (tests, float q)."""
    z = rationalise(q)
    cC, cX, cA = W.rot(z['tC']), W.rot(z['tX']), W.rot(z['tA'])
    C = W.sq_low(z['hu'] + cC[1], z['hv'], cC)
    X = W.sq_low(cX[1], z['xl'], cX)
    A = W.sq_low(z['ax'], F(0), cA)
    Tu = [(x - z['hu'], y) for x, y in C]
    BOX = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1)), (F(0), F(1))]
    xtop = max(y for _, y in X)
    t = dict(hu=z['hu'] > 0, hv=z['hv'] > 0, theta_in_0_5deg=0 <= z['tC'] <= TAN_HALF_5,
             phi_in_0_5deg=0 <= z['tX'] <= TAN_HALF_5, alpha_in_0_90=0 <= z['tA'] < 1,
             side=F(382, 100) <= z['side'] <= W.SHAT_LO, C_meets_box=W.interiors_meet(C, BOX),
             A_in_quadrant=min(x for x, _ in A) >= 0, A_meets_box=W.interiors_meet(A, BOX),
             A_C_disjoint=not W.interiors_meet(A, C), X_top_gt=xtop > z['side'] - 1, X_top_le=xtop <= z['side'],
             X_low_ge1=z['xl'] >= 1, X_in_quadrant=min(x for x, _ in X) >= 0,
             X_meets_Tu=W.interiors_meet(X, Tu), X_C_disjoint=not W.interiors_meet(X, C),
             X_A_disjoint=not W.interiors_meet(X, A))
    qf = np.array([float(z['hu']), float(z['hv']), 2 * math.atan(float(z['tC'])), float(z['xl']),
                   2 * math.atan(float(z['tX'])), float(z['ax']), 2 * math.atan(float(z['tA'])), float(z['side'])])
    return t, qf, {k: str(v) for k, v in z.items()}


def cond_row(q):
    cd = R.conditions(q)
    return {k: float(cd[k]) for k in R.COND + ['Lh', 'beta_deg', 'a_star', 'a_R', 'w_max']}


def describe(q):
    hu, hv, th, xl, phi, ax, al, side = q
    return dict(h_u=hu, h_v=hv, theta_deg=th / DEG, X_low=xl, D=hv + w(th) - xl, phi_deg=phi / DEG, a_x=ax,
                alpha_deg=al / DEG, side=side)


def run_adv(budget, seed=0):
    rng = np.random.default_rng(seed)
    t0 = time.time()
    S = structured_starts(rng, 36)
    print('starts %d  %.0fs' % (len(S), time.time() - t0), flush=True)
    per, res = (budget - (time.time() - t0)) / len(KEYS), {}
    for key in KEYS:
        f, tk = objective(key), time.time()
        vals = np.array([R.conditions(q)[key] for q in S])
        order = list(np.argsort(vals)[:14]) + list(rng.permutation(len(S))[:10])
        best, n_run = None, 0
        for i in order:
            if time.time() - tk > per * 0.8:
                break
            r = minimize(f, S[i], method='Nelder-Mead', options=dict(maxfev=3000, xatol=1e-9, fatol=1e-11))
            n_run += 1
            q = clip(r.x)
            if feasible(q) and (best is None or R.conditions(q)[key] < best[0]):
                best = (float(R.conditions(q)[key]), q)
        for _ in range(3):                                            # polish the best
            r = minimize(f, best[1], method='Nelder-Mead', options=dict(maxfev=3000, xatol=1e-11, fatol=1e-13))
            q = clip(r.x)
            if feasible(q) and R.conditions(q)[key] < best[0]:
                best = (float(R.conditions(q)[key]), q)
        tests, qf, zr = exact_check(best[1])
        cr = cond_row(qf)
        res[key] = dict(min_margin=cr[key], float_min=best[0], exact_H1H3=all(tests.values()), exact_tests=tests,
                        rational=zr, config=describe(qf), conditions=cr, n_runs=n_run,
                        min_constraint=float(R.constraints(qf).min()))
        print('%s min %+.6f exact %s  cfg %s  %.0fs' % (key, cr[key], all(tests.values()),
              {k: round(v, 4) for k, v in describe(qf).items()}, time.time() - t0), flush=True)
    out = dict(mode='adv', budget=budget, seconds=time.time() - t0, n_starts=len(S), results=res)
    json.dump(out, open(os.path.join(RES, 'r1_274_adv.json'), 'w'), indent=1)


CURVE = [(5, 5), (2, 2), (1, 1), (0.5, 0.5), (5, 0), (2, 0), (1, 0), (0.5, 0)]
if os.environ.get('R1_CURVE'):                                        # e.g. R1_CURVE=0.5,0.5;0.5,0 (merged into the json)
    CURVE = [tuple(float(v) for v in z.split(',')) for z in os.environ['R1_CURVE'].split(';')]
HV_CURVE = [float(v) for v in os.environ.get('R1_HV', '0.995').split(',')]


def run_curve(budget):
    """sup over H1-H3 configurations at fixed (theta, phi) of left272's t_L (the square statement): STRIP_2 holds
    at that point iff sup t_L < 0; its margin is -sup t_L.  Starts: h_u x D grid, h_v = 0.995; joint polish."""
    import left272 as LF
    t0, rows = time.time(), []
    per = budget / len(CURVE)
    for thd, phd in CURVE:
        tk, th, phi = time.time(), min(thd * DEG, AMAX), max(min(phd * DEG, AMAX), 2e-6)   # phi >= EPS (H: phi > 0)
        cands = []
        for hu, hv in [(a, b) for a in (0.6, 0.75, 0.85, 0.93) for b in HV_CURVE]:
            ok = []                                                   # D window where X holds C and misses it
            for D in np.linspace(1e-4, 0.2, 100):
                C, X, A, Tu = R.squares(np.array([hu, hv, th, hv + w(th) - D, phi, 5.0, 0.0, 3.85]))
                if min(R.depth(X, Tu), R.Z.poly_gap(X, C)) >= ADV.EPS:
                    ok.append(D)
            for D in (np.quantile(ok, [0.0, 0.3, 0.6, 1.0]) if ok else []):
                q = fill_A(hu, hv, th, hv + w(th) - D, phi, 3.85)
                if feasible(q):
                    Qp, t = LF.best_Q(q, n_polish=1)
                    cands.append((t, q, Qp))
        cands.sort(key=lambda z: -z[0])
        if not cands:
            print('theta %.1f phi %.1f: no feasible start' % (thd, phd), flush=True)
            continue
        best = cands[0]

        def f(z):
            q = np.array([z[0], z[1], th, z[2], phi, z[3], z[4], z[5]])
            v = R.constraints(q) - ADV.EPS
            pen = float(np.sum(np.minimum(v, 0.0) ** 2)) * 1e4 + float(np.sum(v < 0)) * 1e-2
            return -LF.t_L(q, z[6:]) + pen
        for t, q, Qp in cands[:3]:
            if time.time() - tk > per * 0.6:
                break
            z0 = np.concatenate([q[[0, 1, 3, 5, 6, 7]], Qp])
            r = minimize(f, z0, method='Nelder-Mead', options=dict(maxfev=2500, xatol=1e-10, fatol=1e-12))
            qn = np.array([r.x[0], r.x[1], th, r.x[2], phi, r.x[3], r.x[4], r.x[5]])
            if feasible(qn):
                Qn, tn = LF.best_Q(qn, n_polish=6)
                if tn > best[0]:
                    best = (tn, qn, Qn)
        t, q, Qp = best
        tests, qf, zr = exact_check(q)
        rows.append(dict(theta_deg=thd, phi_deg=phd, sup_t=float(t), strip_margin=float(-t), ratio_to_theta2=
                         float(-t / (th ** 2)) if th > 0 else None, config=describe(q), Q=[float(v) for v in Qp],
                         exact_H1H3=all(tests.values()), active=LF.active(q, Qp)[0]))
        print('theta %.1f phi %.1f  sup t_L %+.6f  (%.3f th^2)  exact %s  %.0fs' % (
            thd, phd, t, -t / th ** 2, all(tests.values()), time.time() - t0), flush=True)
    path = os.path.join(RES, 'r1_274_curve.json')
    if os.environ.get('R1_CURVE') and os.path.exists(path):
        done = {(r['theta_deg'], r['phi_deg']) for r in rows}
        rows = [r for r in json.load(open(path))['rows'] if (r['theta_deg'], r['phi_deg']) not in done] + rows
    json.dump(dict(mode='curve', seconds=time.time() - t0, rows=rows), open(path, 'w'), indent=1)


def lower_priority():
    if os.name == 'nt':
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x4000)                                 # BELOW_NORMAL_PRIORITY_CLASS
        k.SetProcessAffinityMask(h, 0xFFFF)


if __name__ == '__main__':
    lower_priority()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'adv'
    sec = float(sys.argv[2]) if len(sys.argv) > 2 else 400.0
    if mode == 'adv':
        run_adv(sec)
    elif mode == 'curve':
        run_curve(sec)
    elif mode == 'page':
        import page274
        page274.main()
