"""A110 chore 1 - the S07 and S02 grain sweeps (one BLAS-pinned process, pure geometry, read-only on
every campaign; A106/A107/A108 modules are imported, never written).

For each shadow the common tilt theta of its load-bearing tilted squares is pinned and EVERYTHING else
(all eleven centres, the upright tilts, the rattler's tilt, s) is re-minimised - A108's relaxed path
generalised - warm-started along the sweep from the exact shadow in both directions.  At every tilt the
landing is rescaled to its exact side sigma (a108lib.sigma), every contact (SAT gap < 1e-6) is listed
with its incidence type, and the Fritz-John multipliers of the fixed-tilt problem (nnls on A107's exact
incidence rows with the pinned tilt columns removed) give the LOADED set = the load path.  Events =
changes of the contact set or of the loaded set between consecutive tilts.  The closed forms
    Lambda(t) = 2 + 2(cos t + sin t)/(1 + sin t cos t)              (the ladder / x-chain)
    Y(t)      = (1 + 3 cos t + sin t + 2 sin t cos t + 2 sin^2 t)/(1 + sin t cos t)   (S07's y-chain)
    A(t)      = the S02 wedge chain (see grain_flood.md section 2.2)
are evaluated alongside.  For S07 the Trump branch is swept upward from Trump's exact packing as well,
so the crossing (the crest) is located from both sides.

Outputs results/sweep_S07.json, results/sweep_S02.json, logs/grain110.log."""
from __future__ import annotations
import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
           'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'
import sys, json, math, time
import numpy as np
from scipy.optimize import minimize, nnls

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A108-s07-certify', 'code'))
import a108lib as A                      # noqa: E402  (adds A107 + A106 to sys.path)
from a108lib import L, MZ, AN            # noqa: E402
import exact as EX                       # noqa: E402

RES = os.path.join(ROOT, 'attempts', 'A110-grain-flood', 'results')
LOGS = os.path.join(ROOT, 'attempts', 'A110-grain-flood', 'logs')
os.makedirs(RES, exist_ok=True); os.makedirs(LOGS, exist_ok=True)
LOG = open(os.path.join(LOGS, 'grain110.log'), 'a', encoding='utf-8')


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True); LOG.write(s + '\n'); LOG.flush()


NV = 34
CONS = MZ.make_cons((), 11)
CTOL = 1e-6          # a contact = SAT / wall gap below this at the sigma-rescaled landing
LTOL = 1e-4          # loaded = per-contact Fritz-John resultant above this


# ------------------------------------------------------------------ closed forms
def Lam(t):
    c, s = math.cos(t), math.sin(t)
    return 2 + 2 * (c + s) / (1 + s * c)


def Ychain(t):
    c, s = math.cos(t), math.sin(t)
    return (1 + 3 * c + s + 2 * s * c + 2 * s * s) / (1 + s * c)


def Awedge(t):
    """S02 chain A: f2 on the top wall, f2 = f1 + (c, s) (full flush), BL(0,1)'s corner (1,2) on f1's
    lower-left edge, TL(0,0)'s corner (1, s-1) on f1's upper-left edge."""
    c, s = math.cos(t), math.sin(t)
    h = (c + s) / 2
    a = (0.5 - (s + h - 1) * c) / s
    b = (0.5 - a * c) / s
    return b + 2 + s + h


# ------------------------------------------------------------------ the fixed-tilt minimiser
def solve_at(theta, z0, pinned, trials=3, seed=0):
    lo = np.array([3.4] + [0.0, 0.0, -3.2] * 11)
    hi = np.array([4.6] + [4.6, 4.6, 3.2] * 11)
    z0 = np.array(z0, float)
    for i in pinned:
        lo[3 + 3 * i] = hi[3 + 3 * i] = theta
        z0[3 + 3 * i] = theta
    best = None
    for k in range(trials):
        z = z0.copy()
        if k:
            rng = np.random.RandomState(1000 * seed + k)
            for i in range(11):
                z[1 + 3 * i] += rng.uniform(-0.02, 0.02)
                z[2 + 3 * i] += rng.uniform(-0.02, 0.02)
            z[0] += 0.01
        z = np.clip(z, lo, hi)
        try:
            r = minimize(lambda v: v[0], z, jac=lambda v: np.eye(1, NV, 0)[0], method='SLSQP',
                         constraints=[{'type': 'ineq', 'fun': CONS}], bounds=list(zip(lo, hi)),
                         options={'maxiter': 400, 'ftol': 1e-14})
        except Exception:
            continue
        if CONS(r.x).min() < -1e-7:
            continue
        ss, cc = A.from107(r.x)
        u, th = A.normalise(ss, cc)
        sg = float(A.sigma(u, th))
        if not math.isfinite(sg):
            continue
        cfg = [(float(u[i][0] * sg), float(u[i][1] * sg), float(th[i])) for i in range(11)]
        if best is None or sg < best[0]:
            best = (sg, cfg, r.x.copy())
    return best


# ------------------------------------------------------------------ contacts + load path
def wall_rows(sq, z, s, nv, tol):
    rows, names = [], []
    c, th = sq.pose(z)
    P = L.corners(c[0], c[1], th)
    for wall in ('left', 'right', 'bottom', 'top'):
        for vi, v in enumerate(P):
            g = {'left': v[0], 'right': s - v[0], 'bottom': v[1], 'top': s - v[1]}[wall]
            if g < tol:
                dV = sq.dvertex(z, vi, nv)
                if wall == 'left':
                    r = dV[0].copy()
                elif wall == 'right':
                    r = -dV[0].copy(); r[0] += 1.0
                elif wall == 'bottom':
                    r = dV[1].copy()
                else:
                    r = -dV[1].copy(); r[0] += 1.0
                rows.append(r); names.append((sq.name, wall + ' wall', vi))
    return rows, names


def analyse_landing(sg, cfg, names, pinned):
    """Contacts (with type and incidences), Fritz-John multipliers with the pinned tilt columns
    removed, loaded set, KKT residual."""
    z = A.to107(sg, cfg)
    sq = AN.build_squares((), 11)
    for q, nm in zip(sq, names):
        q.name = nm
    J, labels, contacts = [], [], []
    for i in range(11):
        for j in range(i + 1, 11):
            g = L.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2])
            if g < CTOL:
                rows, kinds, kind = AN.contact_rows(sq[i], sq[j], z, NV)
                inc = [(k[0], int(k[1]), int(k[2]), float(k[3])) for k in kinds]
                contacts.append(dict(a=names[i], b=names[j], gap=float(g), kind=kind, inc=inc))
                for r in rows:
                    J.append(r); labels.append((names[i], names[j]))
    walls = []
    for i in range(11):
        rows, wn = wall_rows(sq[i], z, sg, NV, CTOL)
        for r, nm in zip(rows, wn):
            J.append(r); labels.append((nm[0], nm[1]))
        for nm in wn:
            walls.append(dict(a=nm[0], wall=nm[1], vertex=nm[2]))
    if not J:
        return dict(contacts=contacts, walls=walls, loaded=[], kkt=None)
    Jm = np.array(J)
    keep = [k for k in range(NV) if k not in {3 + 3 * i for i in pinned}]
    Jk = Jm[:, keep]
    nrm = np.linalg.norm(Jk, axis=1); nrm[nrm == 0] = 1.0
    Jn = Jk / nrm[:, None]
    e = np.zeros(len(keep)); e[0] = 1.0
    lam, res = nnls(Jn.T, e)
    resultant = {}
    for k, lb in enumerate(labels):
        resultant[lb] = resultant.get(lb, np.zeros(len(keep))) + lam[k] * Jn[k]
    force = {f'{a}|{b}': float(np.linalg.norm(v)) for (a, b), v in resultant.items()}
    loaded = sorted(k for k, v in force.items() if v > LTOL)
    return dict(contacts=contacts, walls=walls, force=force, loaded=loaded, kkt=float(res),
                nrows=int(Jm.shape[0]))


def leftmost_vertex(c):
    P = L.corners(c[0], c[1], c[2])
    return min(P, key=lambda p: p[0])


# ------------------------------------------------------------------ one sweep
def sweep(tag, names, s_init, cfg_init, pinned, thetas_deg, seed, markers):
    z = A.to107(s_init, cfg_init)
    out = []
    prev_c, prev_l = None, None
    for k, td in enumerate(thetas_deg):
        t = math.radians(td)
        r = solve_at(t, z, pinned, seed=seed * 1000 + k)
        if r is None:
            log(f'  {tag} {td:8.3f} deg  INFEASIBLE / no landing'); out.append(dict(tilt_deg=td, s=None)); continue
        sg, cfg, z = r[0], r[1], r[2]
        an = analyse_landing(sg, cfg, names, pinned)
        cset = sorted(f"{c['a']}|{c['b']}" for c in an['contacts']) + sorted(f"{w['a']}|{w['wall']}" for w in an['walls'])
        cset = sorted(set(cset))
        ev = []
        if prev_c is not None:
            for x in sorted(set(cset) - set(prev_c)): ev.append('+' + x)
            for x in sorted(set(prev_c) - set(cset)): ev.append('-' + x)
        lev = []
        if prev_l is not None:
            for x in sorted(set(an['loaded']) - set(prev_l)): lev.append('+' + x)
            for x in sorted(set(prev_l) - set(an['loaded'])): lev.append('-' + x)
        prev_c, prev_l = cset, an['loaded']
        rec = dict(tilt_deg=td, s=sg, kkt=an['kkt'], contacts=an['contacts'], walls=an['walls'],
                   force=an.get('force', {}), loaded=an['loaded'], contact_events=ev, load_events=lev,
                   cfg=cfg, Lam=Lam(t), Y=Ychain(t), Awedge=Awedge(t))
        rec.update(markers(cfg, sg))
        out.append(rec)
        log(f"  {tag} {td:8.3f} deg  s={sg:.9f}  Lam={Lam(t):.6f} Y={Ychain(t):.6f} A={Awedge(t):.6f}  "
            f"kkt={an['kkt']:.2e}  ncontacts={len(cset)}  loaded={len(an['loaded'])}"
            + (f"  EVENTS {ev}" if ev else '') + (f"  LOAD {lev}" if lev else ''))
    return out


def s07_markers(cfg, sg):
    v0 = leftmost_vertex(cfg[0])
    return dict(f0_left_vertex=[float(v0[0]), float(v0[1])],
                bl02_lift=float(cfg[7][1] - 2.5), bl01_y=float(cfg[6][1]),
                f3_tilt_deg=float(math.degrees(L.tmod(cfg[3][2]))),
                slot_disp=float(max(abs(cfg[5][0] - 0.5), abs(cfg[5][1] - 0.5), abs(cfg[6][0] - 0.5),
                                    abs(cfg[6][1] - 1.5), abs(cfg[8][0] - 1.5), abs(cfg[8][1] - 0.5),
                                    abs(cfg[9][0] - (sg - 0.5)), abs(cfg[9][1] - 0.5),
                                    abs(cfg[10][0] - (sg - 0.5)), abs(cfg[10][1] - (sg - 0.5)))))


S02_NAMES = ('f0', 'f1', 'f2', 'f3', 'BL(0,0)', 'BL(0,1)', 'BL(1,0)', 'BR(0,0)', 'BR(0,1)', 'TL(0,0)', 'TR(0,0)')
S02_S = 3.886746030
S02_TILT = 48.4351


def s02_init():
    s = S02_S
    th = math.radians(S02_TILT)
    cfg = [(2.167757, 1.519508, th), (1.265647, 2.432705, th), (1.929115, 3.180910, th), (2.621099, 2.454041, th),
           (0.5, 0.5, 0.0), (0.5, 1.5, 0.0), (1.5, 0.5, 0.0), (s - 0.5, 0.5, 0.0), (s - 0.5, 1.5, 0.0),
           (0.5, s - 0.5, 0.0), (s - 0.5, s - 0.5, 0.0)]
    return s, cfg


def s02_markers(cfg, sg):
    v1 = leftmost_vertex(cfg[1])
    return dict(f1_left_vertex=[float(v1[0]), float(v1[1])],
                tl00_y=float(cfg[9][1]), bl01_y=float(cfg[5][1]),
                f0_tilt_deg=float(math.degrees(L.tmod(cfg[0][2]))),
                slot_disp=float(max(max(abs(cfg[k][0] - x), abs(cfg[k][1] - y)) for k, (x, y) in
                                    ((4, (0.5, 0.5)), (5, (0.5, 1.5)), (6, (1.5, 0.5)), (7, (sg - 0.5, 0.5)),
                                     (8, (sg - 0.5, 1.5)), (9, (0.5, sg - 0.5)), (10, (sg - 0.5, sg - 0.5))))))


def frange(a, b, step):
    n = int(round(abs(b - a) / step))
    sgn = 1 if b >= a else -1
    return [round(a + sgn * k * step, 4) for k in range(n + 1)]


def main():
    t0 = time.time()
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    log(f'=== grain110 start {time.strftime("%Y-%m-%d %H:%M:%S")} which={which}')
    if which in ('all', 'S07'):
        s07, cfg07 = EX.exact_float()
        names = list(A.NAMES)
        pinned = [0, 1, 2, 4]                       # f3 (the rattler) keeps a free tilt
        out = {'names': names, 'pinned': [names[i] for i in pinned], 's07': s07}
        log('--- S07 branch, polish at 45 deg')
        r = solve_at(math.pi / 4, A.to107(s07, cfg07), pinned)
        log(f'    polished s = {r[0]:.12f}  (exact {s07:.12f}, diff {r[0]-s07:+.2e})')
        an = analyse_landing(r[0], r[1], names, pinned)
        log('    loaded at 45:', an['loaded'], ' kkt', an['kkt'])
        log('--- S07 branch downward 45 -> 38')
        out['down'] = sweep('S07v', names, s07, cfg07, pinned, frange(45.0, 38.0, 0.1), 1, s07_markers)
        log('--- S07 branch upward 45 -> 62')
        out['up'] = sweep('S07^', names, s07, cfg07, pinned, frange(45.0, 62.0, 0.25), 2, s07_markers)
        st, cfgt, order = A.load_trump()
        tt = math.degrees(cfgt[0][2])
        log(f'--- Trump branch upward {tt:.4f} -> 46 (all five tilted squares pinned, as A108)')
        out['trump_up'] = sweep('TRU^', names, st, cfgt, [0, 1, 2, 3, 4],
                                [round(tt, 4)] + frange(40.3, 46.0, 0.1), 3, s07_markers)
        log(f'--- Trump branch downward {tt:.4f} -> 38')
        out['trump_down'] = sweep('TRUv', names, st, cfgt, [0, 1, 2, 3, 4],
                                  [round(tt, 4)] + frange(40.1, 38.0, 0.1), 4, s07_markers)
        json.dump(out, open(os.path.join(RES, 'sweep_S07.json'), 'w'), indent=1)
        log('wrote results/sweep_S07.json', round(time.time() - t0, 1), 's')
    if which in ('all', 'S02'):
        s02, cfg02 = s02_init()
        names = list(S02_NAMES)
        pinned = [1, 2, 3]                          # f0 (the strut) keeps a free tilt
        out = {'names': names, 'pinned': [names[i] for i in pinned]}
        log('--- S02 polish at 48.4351 deg, all eleven free')
        r = solve_at(math.radians(S02_TILT), A.to107(s02, cfg02), pinned, trials=4)
        log(f'    polished s = {r[0]:.12f}  (gallery {S02_S:.9f}, diff {r[0]-S02_S:+.2e})')
        an = analyse_landing(r[0], r[1], names, pinned)
        log('    contacts at S02:')
        for c in an['contacts']:
            log(f"       {c['a']:8s}-{c['b']:8s} {c['kind']:16s} gap {c['gap']:+.1e} inc {c['inc']}  force {an['force'].get(c['a']+'|'+c['b'], 0):.4f}")
        for w in an['walls']:
            log(f"       {w['a']:8s}-{w['wall']:12s} vertex {w['vertex']}  force {an['force'].get(w['a']+'|'+w['wall'], 0):.4f}")
        log('    loaded:', an['loaded'], ' kkt', an['kkt'])
        out['polish'] = dict(s=r[0], cfg=r[1], analysis=an)
        s02, cfg02 = r[0], r[1]
        log('--- S02 branch downward 48.4351 -> 36')
        out['down'] = sweep('S02v', names, s02, cfg02, pinned, [S02_TILT] + frange(48.4, 36.0, 0.1), 5, s02_markers)
        log('--- S02 branch upward 48.4351 -> 62')
        out['up'] = sweep('S02^', names, s02, cfg02, pinned, [S02_TILT] + frange(48.5, 62.0, 0.25), 6, s02_markers)
        json.dump(out, open(os.path.join(RES, 'sweep_S02.json'), 'w'), indent=1)
        log('wrote results/sweep_S02.json', round(time.time() - t0, 1), 's')
    log(f'=== done in {time.time() - t0:.1f} s')


if __name__ == '__main__':
    main()
