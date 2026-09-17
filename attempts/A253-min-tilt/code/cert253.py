"""A253 task 3: certification.

EXACT (`--mode exact`).  Every reported ring and poker is re-checked in RATIONAL arithmetic, as
A249's `test249.test_ring_exact` does: the tilt is rationalised on the unit circle
(t = tan(theta/2) rounded to 1e-6, cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2)), the deltas, the side
and the poker centre are rounded to 1e-6, the eight ring squares are built in their corner frames
by `geom249`'s formulas and placed by the exact reflections, and then, with Fractions only:
containment in [0, s]^2, the 28 pairwise SAT gaps >= 0, all twelve border cells doubly met, and for
the poker containment, the eight gaps >= 0 and a STRICT overlap with the slot-overlap ribbon.

ONE-PARAMETER (`--mode oneparam`).  The PI's certificate shape: if the room is monotone in the tilt
and theta_min is monotone in s, the family reduces to the CURVE  s -> (theta_min(s), delta(s)) and
capacity <= 2 need only be certified along it.  Over an interval [s0, s1] the ring's members move
by at most rho_i = LIP_C_THETA * dtheta_i + ddelta_i + kappa_i * ds (A251 `family251.deviations`),
so A251's SOUND CORES (`geom251.core_members`, half-side (1/2 - rho)/w(dtheta)) lie inside every
ring of the interval and A237's box-valid PIERCE(2) on those cores certifies capacity <= 2 for the
whole interval.  dtheta, ddelta are MEASURED from the curve at the interval's endpoints (Lemma
CURVE-LIP [C]: the certificate is sound given that bound on the curve's variation).

    python cert253.py --mode exact|oneparam [--boxes N] [--s-lo 3.82] [--s-hi 3.999]
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import geom253 as Z                                                   # noqa: E402
import geom251 as C251                                                # noqa: E402
import family251 as F251                                              # noqa: E402
import geom248 as G                                                   # noqa: E402

RES = os.path.join(ATT, 'results')
STOP = os.path.join(ATT, 'logs', 'STOP')
DEN = 10 ** 6
KAPPA = [F251.KAPPA[c] for c in ('BL', 'BR', 'TR', 'TL') for _ in (0, 1)]


def frac(v):
    return Fr(round(v * DEN), DEN)


def cs(theta):
    t = frac(math.tan(theta / 2.0))
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def rat_wall(theta, delta):
    co, si = cs(theta)
    d = frac(delta)
    L = (Fr(0), d + co)
    V = (L[0] + si, L[1] - co)
    return [V, (V[0] + co, V[1] + si), (V[0] + co - si, V[1] + si + co), L]


def rat_floor(theta, delta):
    co, si = cs(theta)
    d = frac(delta)
    V = (d + si, Fr(0))
    return [V, (V[0] + co, V[1] + si), (V[0] + co - si, V[1] + si + co), (V[0] - si, V[1] + co)]


def place(P, corner, s):
    if corner == 'BL':
        return P
    if corner == 'TL':
        return [(p[0], s - p[1]) for p in P]
    if corner == 'BR':
        return [(s - p[0], p[1]) for p in P]
    return [(s - p[0], s - p[1]) for p in P]


def rat_poker(pose):
    co, si = cs(pose[2])
    cx, cy = frac(pose[0]), frac(pose[1])
    h = Fr(1, 2)
    return [(cx + co * a - si * b, cy + si * a + co * b)
            for a, b in ((-h, -h), (h, -h), (h, h), (-h, h))]


def exact_gap(P, Q):
    best = None
    for poly in (P, Q):
        for k in range(4):
            e = (poly[(k + 1) % 4][0] - poly[k][0], poly[(k + 1) % 4][1] - poly[k][1])
            n = (e[1], -e[0])
            a = [p[0] * n[0] + p[1] * n[1] for p in P]
            b = [q[0] * n[0] + q[1] * n[1] for q in Q]
            g = max(min(b) - max(a), min(a) - max(b))
            best = g if best is None or g > best else best
    return best


def rect(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def cells(s):
    one = Fr(1)
    out = {}
    for c, (X, Y) in (('BL', ((Fr(0), one), (Fr(0), one))), ('BR', ((s - 1, s), (Fr(0), one))),
                      ('TR', ((s - 1, s), (s - 1, s))), ('TL', ((Fr(0), one), (s - 1, s)))):
        out[c + '00'] = (X, Y)
        out[c + '01'] = (X, (one, Fr(2)) if Y[0] == 0 else (s - 2, s - 1))
        out[c + '10'] = ((one, Fr(2)) if X[0] == 0 else (s - 2, s - 1), Y)
    return out


def ribbon(s, wall):
    a, b = s - 2, Fr(2)
    return [(Fr(0), Fr(1), a, b), (a, b, Fr(0), Fr(1)), (s - 1, s, a, b), (a, b, s - 1, s)][wall]


def exact_ring(x, s_float, pose=None, wall=None):
    """the full rational check; returns a dict of exact minima (as floats) and the verdicts."""
    s = frac(s_float)
    sq = []
    for k, c in enumerate(('BL', 'BR', 'TR', 'TL')):
        tB, dB, tA, dA = x[4 * k:4 * k + 4]
        sq.append(place(rat_wall(tB, dB), c, s))
        sq.append(place(rat_floor(tA, dA), c, s))
    inside = min(min(min(p[0], p[1], s - p[0], s - p[1]) for p in P) for P in sq)
    gaps = [exact_gap(sq[i], sq[j]) for i in range(8) for j in range(i)]
    met = {}
    for name, (X, Y) in cells(s).items():
        R = rect(X[0], X[1], Y[0], Y[1])
        met[name] = sum(1 for P in sq if exact_gap(P, R) < 0)
    out = {'exact_containment': float(inside), 'exact_min_gap': float(min(gaps)),
           'cells_doubly_met': bool(min(met.values()) >= 2), 'cell_counts': met,
           'ring_ok': bool(inside >= 0 and min(gaps) >= 0 and min(met.values()) >= 2)}
    if pose is not None:
        K = rat_poker(pose)
        kin = min(min(p[0], p[1], s - p[0], s - p[1]) for p in K)
        kg = [exact_gap(K, P) for P in sq]
        rb = exact_gap(K, rect(*ribbon(s, wall)))
        out.update({'poker_containment': float(kin), 'poker_min_gap': float(min(kg)),
                    'poker_ribbon_gap': float(rb),
                    'poker_ok': bool(kin >= 0 and min(kg) >= 0 and rb < 0)})
    return out


# ------------------------------------------------------------------ the one-parameter certificate
def curve_ring(s, sg, d0, tau_deg, maxiter=1200, wall=None):
    import mintilt253 as M
    sig = [int(c) for c in sg]
    r = M.joint_best(tau_deg * Z.DEG, sig, s, d0=d0, maxiter=maxiter,
                     walls=(wall,) if wall is not None else (0, 1, 2, 3))
    return r


def theta_min_at(s, sg, d0, lo, hi, iters=10, maxiter=1000, wall=None):
    import mintilt253 as M
    l, h, best, hist = M.bisect(s, sg, lo, hi, d0, iters=iters, maxiter=maxiter, tries=1,
                                kind='joint')
    return l, h, best


def box_cert(x_mid, s_mid, dth, ddel, ds, step_deg=2.0, tol=1e-12):
    """A251's sound cores for the interval + A237 box-valid PIERCE(1) and (2)."""
    poses = [tuple(map(float, G.pose_of(V))) for V in Z.polys(x_mid, s_mid)]
    rhos = [C251.LIP_C_THETA * dth[i] + ddel[i] + KAPPA[i] * ds for i in range(8)]
    mem = C251.core_members(poses, rhos, dth)
    if min(m[3] for m in mem) <= 0:
        return {'cores_empty': True, 'rho_max': max(rhos)}
    free = C251.free_bins(mem, s_mid, step_deg)
    out = {'cores_empty': False, 'rho_max': max(rhos), 'core_half_min': min(m[3] for m in mem)}
    r1, p1 = C251.best_pierce2(mem, s_mid, free, r=0.9, g=7) if False else (None, None)
    for k in (1, 2):
        import room253 as R
        res, pts = R.pierce_opt(mem, s_mid, k, step_deg, restarts=3, seed=k, maxiter=900,
                                seeds=())
        out['pierce%d' % k] = {'residual': res, 'certifies': bool(res <= tol), 'points': pts}
        if res <= tol:
            break
    return out


def mode_oneparam(a):
    """the ONE-PARAMETER certificate: the tilt is FIXED (theta_min(s) = 0, so the curve the family
    reduces to is s -> the ring at a fixed common tilt) and only s varies.  Over each s-interval
    the members move by rho_i = LIP_C_THETA*0 + ddelta_i + kappa_i*ds, so A251's sound cores are
    large and A237's box-valid PIERCE(1) / (2) is cheap."""
    import mintilt253 as M
    fn = os.path.join(RES, 'cert253_oneparam.jsonl')
    done = set()
    if os.path.exists(fn):
        done = {(json.loads(l)['box'], json.loads(l)['tau_deg'])
                for l in open(fn, encoding='utf-8') if l.strip()}
    sg = a.sigma
    n, h = a.boxes, (a.s_hi - a.s_lo) / a.boxes
    x0 = Z.shat_ring()
    for tau in [float(v) for v in a.taus.split(',')]:
        d0 = [x0[1], x0[3], x0[5], x0[7], x0[9], x0[11], x0[13], x0[15]]
        for i in range(n):
            if os.path.exists(STOP):
                return print('STOP present', flush=True)
            if (i, tau) in done:
                continue
            t0 = time.time()
            s0, s1 = a.s_lo + i * h, a.s_lo + (i + 1) * h
            sm = 0.5 * (s0 + s1)
            got = {}
            for tag, ss in (('mid', sm), ('lo', s0), ('hi', s1)):
                r = M.joint_best(tau * Z.DEG, [int(c) for c in sg], ss, d0=d0,
                                 maxiter=a.maxiter, tries=1)
                got[tag] = r
                if r['M'] > 0:
                    d0 = r['deltas']
            row = {'box': i, 'tau_deg': tau, 's0': s0, 's1': s1, 's_mid': sm, 'sigma': sg,
                   'M': {t: got[t]['M'] for t in got}, 'seconds': time.time() - t0}
            if min(got[t]['M'] for t in got) <= 0:
                row['ok'] = False
                row['why'] = 'no ring at this tilt across the interval'
            else:
                xm = Z.x_of(tau * Z.DEG, [int(c) for c in sg], got['mid']['deltas'])
                ddel = [a.safety * max(abs(got[t]['deltas'][j] - got['mid']['deltas'][j])
                                       for t in ('lo', 'hi')) for j in range(8)]
                cert = box_cert(xm, sm, [0.0] * 8, ddel, 0.5 * h, step_deg=a.step_deg)
                row.update({'ddelta_max': max(ddel), 'ds': 0.5 * h, 'cert': cert, 'x_mid': xm,
                            'pose': got['mid']['pose'], 'wall': got['mid']['wall']})
                row['ok'] = bool(not cert.get('cores_empty') and
                                 (cert.get('pierce1', {}).get('certifies') or
                                  cert.get('pierce2', {}).get('certifies')))
                row['seconds'] = time.time() - t0
            with open(fn, 'a', encoding='utf-8') as f:
                f.write(json.dumps(row) + '\n')
            print('box %2d tau %5.2f [%.4f, %.4f]  ok %s  pierce1 %s pierce2 %s (%.0fs)'
                  % (i, tau, s0, s1, row.get('ok'),
                     row.get('cert', {}).get('pierce1', {}).get('residual'),
                     row.get('cert', {}).get('pierce2', {}).get('residual'),
                     row['seconds']), flush=True)
    print('ONEPARAM DONE', flush=True)


def mode_exact(a):
    """rational re-verification of every ring + poker the curve rows report as feasible."""
    import mintilt253 as M
    out = []
    src = [r for r in M.rows('mintilt253_curve.jsonl') if r.get('pose') and r['M'] > 0]
    src += [r['best'] for r in M.rows('mintilt253_bisect.jsonl')
            if r['kind'] == 'joint' and r.get('best') and r['best'].get('pose')]
    for r in src:
        sg = r.get('sigma', a.sigma)
        s = float(r['side']) if 'side' in r else None
        if s is None:
            continue
        x = Z.x_of(r['tau_deg'] * Z.DEG, [int(c) for c in sg], r['deltas'])
        e = exact_ring(x, s, r['pose'], r['wall'])
        e.update({'side': r['side'], 'sigma': sg, 'tau_deg': r['tau_deg'], 'float_M': r['M'],
                  'wall': r['wall']})
        out.append(e)
        print('exact s=%s tau %6.3f  ring_ok %s (gap %+.2e) poker_ok %s (gap %+.2e, ribbon %+.2e)'
              % (r['side'], r['tau_deg'], e['ring_ok'], e['exact_min_gap'], e.get('poker_ok'),
                 e.get('poker_min_gap', 0), e.get('poker_ribbon_gap', 0)), flush=True)
    json.dump(out, open(os.path.join(RES, 'cert253_exact.json'), 'w', encoding='utf-8'), indent=1)
    print('EXACT DONE (%d rows)' % len(out), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='exact')
    ap.add_argument('--boxes', type=int, default=20)
    ap.add_argument('--s-lo', type=float, default=3.82, dest='s_lo')
    ap.add_argument('--s-hi', type=float, default=3.999, dest='s_hi')
    ap.add_argument('--iters', type=int, default=9)
    ap.add_argument('--maxiter', type=int, default=900)
    ap.add_argument('--step-deg', type=float, default=2.0, dest='step_deg')
    ap.add_argument('--safety', type=float, default=1.5)
    ap.add_argument('--sigma', default='00110011')
    ap.add_argument('--taus', default='14.545,6,2')
    a = ap.parse_args()
    Z.belownormal()
    {'exact': mode_exact, 'oneparam': mode_oneparam}[a.mode](a)


if __name__ == '__main__':
    main()
