r"""A279 [M]: the NEST end of the FLOAT2 residual.  4-square model of A261/A277 (local261 imported, never edited):
C, D floaters meeting the open box, X wall toucher and Y floor toucher missing it, every drop blocked, pair gaps,
containment.  New terms: (NEST) margin = min(alpha_- - eta_+, xi_- - alpha_+) over the separator arcs (degrees/100),
and -J_any(F) for F in {C, D}: J_any = sup over wall-touching cells of ANY pose (jam261's fine grid 1 deg x 0.01 +
local refine) of min(gaps to the other three, depth into F).  sup t > 0 <=> a NEST quadruple with no any-pose landing
cell (a genuine residual point of L, to be shadow-tested); sup t <= 0 <=> [M] every NEST quadruple has a landing cell.
--hv LO forces h_v(D) >= LO (the high-D end).  One python, BelowNormal, resumable (rows keyed by (mode, seed)).
    python nest279.py --restarts 10 --seeds 1,2,3 [--hv 0.3]  -> results/nest279.jsonl"""
import argparse, json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
for a_ in ('A261-box-meeters', 'A259-normal-room', 'A258-normal-ring'):
    sys.path.insert(0, os.path.join(ROOT, 'attempts', a_, 'code'))
os.environ.setdefault('JAM_COARSE', '1'); import local261 as L; import jam261 as J; import geo258 as G8; import geom259 as Z      # noqa: E401,E702
OUT = os.path.join(HERE, '..', 'results', 'nest279.jsonl')
SPEC, MEET, NOTMEET = 'C:F D:F X:V Y:H', ['C', 'D'], ['X', 'Y']
ANG = np.radians(np.arange(0.05, 90.0, 0.1)); NRM = np.stack([-np.sin(ANG), np.cos(ANG)], 1)   # normals of +slope lines


def arc(Up, Lo):
    """slope angles (deg) of the lines separating Up (upper-left, + side) from Lo: ((min, max), peak) or (None, peak).
    Grid 0.1 deg, peak refined by golden section, endpoints by bisection (the margin is a min of sinusoids)."""
    f = lambda a: float((Up @ np.array([-math.sin(a), math.cos(a)])).min() - (Lo @ np.array([-math.sin(a), math.cos(a)])).max())
    m = (Up @ NRM.T).min(0) - (Lo @ NRM.T).max(0)
    k = int(np.argmax(m)); lo_, hi_ = ANG[max(k - 1, 0)], ANG[min(k + 1, len(ANG) - 1)]
    for _ in range(40):                                                  # golden section on [lo_, hi_]
        c1, c2 = hi_ - 0.618034 * (hi_ - lo_), lo_ + 0.618034 * (hi_ - lo_)
        if f(c1) < f(c2): lo_ = c1
        else: hi_ = c2
    apk = 0.5 * (lo_ + hi_); peak = f(apk)
    if peak < -1e-9:
        return None, peak
    def root(a_in, a_out):                                               # f(a_in) >= 0 > f(a_out)
        for _ in range(40):
            mid = 0.5 * (a_in + a_out)
            if f(mid) >= 0: a_in = mid
            else: a_out = mid
        return a_in
    ok = np.nonzero(m >= 0)[0]
    a0 = root(apk, ANG[ok[0]] - math.radians(0.1)) if len(ok) else root(apk, apk - math.radians(0.1))
    a1 = root(apk, ANG[ok[-1]] + math.radians(0.1)) if len(ok) else root(apk, apk + math.radians(0.1))
    return (math.degrees(a0), math.degrees(a1)), peak


def nest(P):
    """P = [C, D, X, Y]; returns (margin, arcs).  margin > 0 <=> eta_+ < alpha_- and alpha_+ < xi_- (then in deg/100);
    if some pair has no positive-slope separator of the right orientation, margin = the least (negative) peak gap
    along the positive-slope normals -- continuous in the poses (no plateau for the optimiser)."""
    (al, pa), (et, pe), (xi, px) = arc(P[0], P[1]), arc(P[1], P[3]), arc(P[2], P[0])
    arcs = dict(alpha=al, eta=et, xi=xi, peaks=[pa, pe, px])
    if al is None or et is None or xi is None:
        return min(pa, pe, px), arcs
    return min(al[0] - et[1], xi[0] - al[1]) / 100.0, arcs


def j_any(P, i):
    """sup over any-pose wall cells of min(gaps to P[j], j != i; depth into P[i]); grid argmax + Nelder-Mead refine."""
    g = [J.gaps(P[j]) for j in range(len(P))]
    v = np.minimum.reduce([g[j] for j in range(len(P)) if j != i] + [-g[i]])
    k = int(np.argmax(v)); wall = 'x=0' if k < len(J.CELLS) // 2 else 'y=0'
    th0, p0 = float(J.CTH[k]), float(J.POS[(k % (len(J.CELLS) // 2)) % len(J.POS)])
    def val(z):
        th, p = z; wv = abs(math.cos(th)) + abs(math.sin(th))
        c = (0.5 * wv, 0.5 * wv + p) if wall == 'x=0' else (0.5 * wv + p, 0.5 * wv)
        T = L.verts(c[0], c[1], th)
        return min([G8.sat_gap(T, P[j]) for j in range(len(P)) if j != i] + [G8.depth(P[i], T)])
    z = np.array([th0, p0])
    if v[k] > -0.06:
        r = minimize(lambda z: -val(z), [th0, max(p0, 0.0)], method='Nelder-Mead', options=dict(xatol=1e-6, fatol=1e-9, maxiter=150))
        z = r.x if -r.fun > float(v[k]) and r.x[1] >= 0 else z
    return float(val(z)), dict(wall=wall, tilt_deg=math.degrees(z[0]) % 90.0, pos=float(z[1]))


def objective(x, sq, hv, stage='nest'):
    """stage 'nest': min(local terms, NEST margin) -- is a NEST quadruple realisable at all?  stage 'cell': also -J_any."""
    t, ps, nm = L.terms(x, sq, MEET, NOTMEET); m = min(t)
    if hv is not None:
        m = min(m, ps[1][1] - 0.5 * L.w(ps[1][2]) - hv)                  # h_v(D) >= hv
    P = [L.verts(*p) for p in ps]
    m = min(m, nest(P)[0])
        if stage == 'cell' and m > -0.05:
            m = min(m, -j_any(P, 0)[0], -j_any(P, 1)[0])
    return -m


def seed(sq, rng, hv):
    if rng.uniform() < 0.5:                                              # half the starts: local261-style random
        return np.concatenate([np.append(rng.uniform(0.0, 1.1, 2 if s_[1] == 'F' else 1), rng.uniform(0, math.pi / 2)) for s_ in sq])
    """C at the wall meeting the box, D high and to the right, Y under D, X above C (the NEST picture) + noise."""
    hvD = rng.uniform(0.3, 0.9) if hv is None else rng.uniform(hv, min(hv + 0.4, 0.95))
    x = [math.sqrt(rng.uniform(0.01, 0.2)), math.sqrt(rng.uniform(0.6, 1.2)), rng.uniform(0.05, 0.8),      # C
         math.sqrt(rng.uniform(0.3, 1.0)), math.sqrt(hvD), rng.uniform(0.05, 0.8),                           # D
         math.sqrt(rng.uniform(1.5, 2.3)), rng.uniform(0.1, 0.9),                                            # X
         math.sqrt(rng.uniform(1.0, 1.6)), rng.uniform(0.1, 1.4)]                                            # Y
    return np.array(x)


def run(restarts, sd, hv, stage):
    sq, dim = L.layout(SPEC); rng = np.random.default_rng(sd); best, bx, t0 = -1e9, None, time.time()
    for r in range(restarts):
        x0 = seed(sq, rng, hv)
        opt = dict(maxiter=4000 if stage == 'nest' else 1500, xatol=1e-9, fatol=1e-11, adaptive=True)
        res = minimize(objective, x0, args=(sq, hv, stage), method='Nelder-Mead', options=opt)
        res = minimize(objective, res.x, args=(sq, hv, stage), method='Nelder-Mead', options=opt)
        if -res.fun > best:
            best, bx = -res.fun, res.x
    t, ps, names = L.terms(bx, sq, MEET, NOTMEET); P = [L.verts(*p) for p in ps]
    nm, arcs = nest(P); jC, cC = j_any(P, 0); jD, cD = j_any(P, 1)
    return dict(mode=('hv%.2f' % hv if hv is not None else 'free') + '/' + stage, seed=sd, restarts=restarts, sup_margin=float(best),
                seconds=round(time.time() - t0, 1), poses={n: list(map(float, p)) for n, p in zip(names, ps)},
                local_min=float(min(t)), nest_margin_deg=nm * 100, arcs=arcs, J_C=jC, cell_C=cC, J_D=jD, cell_D=cD,
                hD=[float(P[1][:, 0].min()), float(P[1][:, 1].min())], hC=[float(P[0][:, 0].min()), float(P[0][:, 1].min())],
                check=L.check_witness(ps, sq, MEET, NOTMEET), verdict='RESIDUAL-POINT' if best > 1e-6 else 'NO-WITNESS')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--restarts', type=int, default=10)
    ap.add_argument('--seeds', default='1,2,3'); ap.add_argument('--hv', type=float, default=None); ap.add_argument('--stage', default='nest'); a = ap.parse_args()
    Z.belownormal()
    done = {(json.loads(l)['mode'], json.loads(l)['seed']) for l in open(OUT)} if os.path.exists(OUT) else set()
    mode = ('hv%.2f' % a.hv if a.hv is not None else 'free') + '/' + a.stage
    STOP = os.path.join(HERE, '..', 'logs', 'STOP')
    for sd in map(int, a.seeds.split(',')):
        if (mode, sd) in done or os.path.exists(STOP):
            continue
        row = run(a.restarts, sd, a.hv, a.stage)
        with open(OUT, 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(mode, sd, row['verdict'], '%.6f' % row['sup_margin'], 'J_C %.4f J_D %.4f' % (row['J_C'], row['J_D']), row['cell_D'], row['seconds'], 's', flush=True)
