"""k0dir2_87.py -- A87 chore: directed K0-BLOCKED search under the STRICT
intruder convention, with the depth floor as a HYPOTHESIS rather than an artefact.

Background.  k0dir87.py answered "is there an FJ point inside K0-BLOCKED?" with a
BLOCK test at TOL_BLOCK = 1e-9 (any certified intrusion counts) and an artificial
constrained-phase floor EPS_KEEP = 1e-4.  Its record (3.9854837) has TL/TR second
intruders at 8.0e-9 / 1.7e-8 -- tangencies, not blocks -- and the six K0-BLOCKED
survivors of degen87 sit exactly on EPS_KEEP.  So under the strict convention of
A85's strict85 ("MEETS iff certified depth > 1e-6") NO K0-BLOCKED packing below
side 4.000004 was known.

Question answered here.  Does ANY strictly K0-BLOCKED packing exist below side 4?
The K0-BLOCKED region is redefined per run as

    K0-BLOCKED(delta)  <=>  every one of the four closed unit corner slots is met
                            by >= 2 squares at CERTIFIED intrusion depth >= delta

for delta in {1e-6, 1e-4, 1e-3, 1e-2}, and the whole k0dir87 pipeline (A85 pair
census seeds with two intruders per corner, guarded free descent, descent confined
to the region, deep re-run walking the constraint down onto the floor, exact
interval verification of the record) is re-run once per floor.  The FREE flows are
also run as flows in their own right: their exit side is the side at which some
corner drops below 2 strict meeters.

Writes only  results/k0dir2_87.*  notes/k0dir2_87.md  logs/k0dir2_87.log.
Usage: python k0dir2_87.py {selftest|canary|run [nseeds] [wall]|report}
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import math
import random
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
A87 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A87, '..'))
A85 = os.path.join(ATT, 'A85-k0-route')

sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A85, 'code'))

import cp85                       # noqa: E402
import fjpolish87 as F            # noqa: E402
import k0blocked87 as KB          # noqa: E402
import t3lib as T                 # noqa: E402
import k0dir87 as K               # noqa: E402  (geometry, seeds, SQP pieces)

RESULTS = os.path.join(A87, 'results')
NOTES = os.path.join(A87, 'notes')
LOGS = os.path.join(A87, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

OUT_JL = os.path.join(RESULTS, 'k0dir2_87.jsonl')
OUT_JS = os.path.join(RESULTS, 'k0dir2_87.json')
OUT_DEEP = os.path.join(RESULTS, 'k0dir2_87.deep.jsonl')
OUT_REC = os.path.join(RESULTS, 'k0dir2_87.records.json')
OUT_MD = os.path.join(NOTES, 'k0dir2_87.md')

N = K.N
H = K.H
HALFPI = K.HALFPI
CORNERS = K.CORNERS
CSGN = K.CSGN
S_HAT = K.S_HAT
S0F = K.S0F

FLOORS = (1e-6, 1e-4, 1e-3, 1e-2)

# The constraint is pinned slightly INSIDE the floor so that the strictify step
# (fjpolish87.inflate) cannot push an accepted iterate back below it.  Acceptance
# is always judged at the exact floor, so this only makes the reported sides
# conservative (upper bounds on the true infimum at the floor).
KEEP_MARGIN = 1.02
POOL_MARGIN = 2.0        # census pairs are pre-filtered at depth >= POOL_MARGIN*delta

TRUST0 = K.TRUST0
TRUST_MIN = K.TRUST_MIN
ROUNDS_FREE = 22
ROUNDS_CONF = 34
ROUNDS_DEEP = 120
DEEP_N = 12
VERIFY_N = 6             # how many endpoints per floor get the exact verification


# ================================================== strict float BLOCK test

def k0_state_d(x, delta):
    """The float strict test on the TIGHT bounding box.

    depth = -gap; a square MEETS a slot iff depth >= delta.  K0-BLOCKED(delta)
    iff every one of the four slots has >= 2 meeters."""
    gaps, _a, _g, anch = K.slot_gaps(x, use_bbox=True)
    depth = -gaps
    nb = (depth >= delta).sum(axis=1)
    order = np.argsort(-depth, axis=1)
    m1 = np.array([depth[k, order[k, 0]] for k in range(4)])
    m2 = np.array([depth[k, order[k, 1]] for k in range(4)])
    blockers = [sorted(int(j) for j in range(N) if depth[k, j] >= delta)
                for k in range(4)]
    return dict(n_block=[int(v) for v in nb], depth=depth, m1=m1, m2=m2,
                blockers=blockers, blocked=bool(nb.min() >= 2),
                min_m2=float(m2.min()),
                anchors={k: [float(v) for v in anch[k]] for k in CORNERS})


def is_blocked_d(x, delta):
    gaps, _a, _g, _an = K.slot_gaps(x, use_bbox=True)
    return bool(((-gaps) >= delta).sum(axis=1).min() >= 2)


# ============================================ exact certified BLOCK test at floor

def exact_blocked_test_d(zfrac, delta, ladder=KB.DPS_LADDER):
    """Certified per-corner meeter counts at the floor, against the INNER slot.

    Same sound inner-slot construction as k0dir87.exact_blocked_test (a rational
    rectangle CONTAINED in the true unit slot for every realisation of the
    interval bounding box, so a certified overlap with it is a certified overlap
    with the true slot), but the bar is the floor: square j MEETS the slot iff its
    certified depth is >= delta, i.e. gap.b <= -delta.  gap.a > -delta certifies it
    does NOT meet.  Anything in between is UNKNOWN and the dps ladder is climbed."""
    per = None
    dps = ladder[0]
    unknown = 0
    for dps in ladder:
        KB.set_dps(dps)
        pt = KB.ivpt(zfrac)
        Q = KB.all_corners_iv(pt)
        xlo, xhi, ylo, yhi = KB.bbox_iv(Q)
        one = Fraction(1)
        XA, XB = KB._lo_frac(xlo), KB._hi_frac(xlo)
        XC, XD = KB._lo_frac(xhi), KB._hi_frac(xhi)
        YA, YB = KB._lo_frac(ylo), KB._hi_frac(ylo)
        YC, YD = KB._lo_frac(yhi), KB._hi_frac(yhi)
        xs = {0: (XB, XA + one), 1: (XD - one, XC)}
        ys = {0: (YB, YA + one), 1: (YD - one, YC)}
        per = {}
        unknown = 0
        for cn in CORNERS:
            sx, sy = CSGN[cn]
            rect = (xs[sx][0], xs[sx][1], ys[sy][0], ys[sy][1])
            blockers, unk, dlo = [], [], []
            for j in range(11):
                g = K._rect_square_gap(rect, Q[j], pt[3 * j + 2])
                dlo.append(float(-g.b))      # certified LOWER bound on the depth
                if g.b <= -delta:
                    blockers.append(j)
                elif g.a > -delta:
                    continue
                else:
                    unk.append(j)
            unknown += len(unk)
            dep = sorted((dlo[j] for j in blockers), reverse=True)
            per[cn] = {'meeters': blockers, 'unknown': unk,
                       'n_meet_certified': len(blockers),
                       'certified_depths': dep,
                       'd1': dep[0] if dep else None,
                       'd2': dep[1] if len(dep) > 1 else None,
                       'rect': [str(v) for v in rect]}
        if unknown == 0:
            break
    KB.set_dps(30)
    cert = [per[c]['n_meet_certified'] for c in CORNERS]
    return {'delta': delta, 'per_corner': per, 'dps': dps, 'n_unknown': unknown,
            'n_meet_certified': cert,
            'n_unknown_per_corner': [len(per[c]['unknown']) for c in CORNERS],
            'min_n_meet_certified': min(cert),
            'K0_BLOCKED_certified': bool(min(cert) >= 2 and unknown == 0),
            'd2_per_corner': [per[c]['d2'] for c in CORNERS],
            'd1_per_corner': [per[c]['d1'] for c in CORNERS]}


# ==================================================== depth-annotated pair pool

_BASE_POOL = None


def base_pool(rng, n=3000, log=None):
    """Census pairs with the BL-frame min intrusion depth attached."""
    global _BASE_POOL
    if _BASE_POOL is None or len(_BASE_POOL) < n:
        t0 = time.time()
        out = list(_BASE_POOL) if _BASE_POOL else []
        while len(out) < n:
            p = K.draw_corner_pair(rng)
            if p is None:
                continue
            a, b = p
            dd = []
            for (cx, cy, t) in (a, b):
                V, _G = K.slot_rows(np.array([[cx, cy]]), np.array([t]), (0.0, 0.0))
                dd.append(-float(V[0].max()))
            out.append((a, b, min(dd)))
        _BASE_POOL = out
        if log:
            log('pair pool: %d pairs in %.0fs; min-depth quantiles %s'
                % (len(out), time.time() - t0,
                   ' '.join('%.4f' % v for v in
                            np.percentile([e[2] for e in out], [5, 25, 50, 75, 95]))))
    return _BASE_POOL


def pool_for(delta, rng, log=None):
    P = base_pool(rng, log=log)
    sub = [(a, b) for (a, b, d) in P if d >= POOL_MARGIN * delta]
    if log:
        log('floor %.0e: %d/%d census pairs survive the depth filter (>= %.1e)'
            % (delta, len(sub), len(P), POOL_MARGIN * delta))
    return sub


def build_seed_d(rng, sub, delta, tries=500, outer=10):
    """11 squares: 2 per corner, all eight at depth >= delta, + 3 in the middle."""
    if not sub:
        return None
    for _o in range(outer):
        ss = rng.uniform(4.5, 5.5)
        cs, ts = [], []
        for cn in CORNERS:
            a, b = sub[rng.randrange(len(sub))]
            for (cx, cy, t) in (a, b):
                X, Y, T_ = K._corner_map(cn, cx, cy, t, ss)
                cs.append([X, Y]); ts.append(T_)
        bad = False
        for i in range(8):
            for j in range(i + 1, 8):
                if i // 2 == j // 2:
                    continue
                if not K._pair_disjoint((cs[i][0], cs[i][1]), ts[i],
                                        (cs[j][0], cs[j][1]), ts[j]):
                    bad = True; break
            if bad:
                break
        if bad:
            continue
        ok = True
        for _k in range(3):
            got = False
            for _t in range(tries):
                T_ = rng.uniform(0.0, HALFPI)
                ee = H * (abs(math.cos(T_)) + abs(math.sin(T_)))
                X = rng.uniform(ee, ss - ee); Y = rng.uniform(ee, ss - ee)
                if all(K._pair_disjoint((X, Y), T_, (cs[q][0], cs[q][1]), ts[q])
                       for q in range(len(cs))):
                    cs.append([X, Y]); ts.append(T_); got = True
                    break
            if not got:
                ok = False; break
        if not ok:
            continue
        x = cp85.pack(np.array(cs), np.array(ts), float(ss))
        ov, cv = K.feas(x)
        if ov > 1e-12 or cv > 1e-12:
            continue
        if not is_blocked_d(x, delta):
            continue
        return x
    return None


# ============================================================ confined SQP flow

def sqp_step_d(x, keep_k0, delta_tr, eps_keep, maxiter=35):
    """One trust-region SLSQP move (k0dir87.sqp_step with the K0 depth floor
    supplied explicitly instead of read off a module constant)."""
    ov, _aux = cp85.pair_overlaps(x)
    kfix = np.argmin(ov, axis=1)
    cp = K._Cache(lambda z, k=kfix: K.pair_con_fast(z, k))
    cc = K._Cache(K.cont_con_fast)
    cons = [dict(type='ineq', fun=cp.val, jac=cp.jac),
            dict(type='ineq', fun=cc.val, jac=cc.jac)]
    sel = K.select_k0(x)
    if keep_k0:
        K.EPS_KEEP = eps_keep          # k0dir87.k0_cons reads this global
        ck = K._Cache(lambda z, q=sel: K.k0_cons(z, q))
        cons.append(dict(type='ineq', fun=ck.val, jac=ck.jac))
    bnds = [(v - delta_tr, v + delta_tr) for v in x]
    e = np.eye(3 * N + 1)[3 * N]
    try:
        res = minimize(lambda z: z[3 * N], x, jac=lambda z: e, constraints=cons,
                       bounds=bnds, method='SLSQP',
                       options=dict(maxiter=maxiter, ftol=1e-14))
    except Exception:
        return None, sel
    y = res.x.copy()
    if not np.all(np.isfinite(y)):
        return None, sel
    return y, sel


def _blocked_feasible_d(w, delta):
    ws, sg, ov, cv = K.strictify(w)
    good = bool(np.isfinite(sg) and ov <= 1e-11 and cv <= 1e-9)
    return ws, sg, good, (good and is_blocked_d(ws, delta))


def _bisect_exit_d(x, y, delta, nit=44):
    lo, hi = 0.0, 1.0
    for _ in range(nit):
        m = 0.5 * (lo + hi)
        _w, _s, good, blk = _blocked_feasible_d(x + m * (y - x), delta)
        if good and blk:
            lo = m
        else:
            hi = m
    return (_blocked_feasible_d(x + lo * (y - x), delta),
            _blocked_feasible_d(x + hi * (y - x), delta))


def _exit_record_d(x_ok, y_bad, delta):
    a, b = _bisect_exit_d(x_ok, y_bad, delta)
    xe, sge, ok_e, blk_e = a
    xb, sgb, _ok_b, _blk_b = b
    st0 = k0_state_d(xe, delta); st1 = k0_state_d(xb, delta)
    em = K.exit_mode(st0, st1)
    em['sigma_exit'] = float(sge)
    em['sigma_after_exit'] = float(sgb)
    em['exit_feasible'] = bool(ok_e)
    em['exit_blocked'] = bool(blk_e)
    em['n_block_exit'] = st0['n_block']
    em['n_block_after'] = st1['n_block']
    em['m2_exit'] = [float(v) for v in st0['m2']]
    return em


def sqp_flow_d(x0, delta, keep_k0, rounds, eps_keep=None, delta0=TRUST0):
    """Feasible trust-region descent on the side under the strict convention.

    keep_k0=False: the strict test is only a MONITOR -- the flow stops and the
    exit is recorded the first time a step would leave K0-BLOCKED(delta).
    keep_k0=True: the two deepest intruders per corner are pinned to depth >=
    eps_keep and the step is shrunk instead of leaving.  Acceptance is always
    judged by the strict test AT THE FLOOR on the strictified iterate."""
    if eps_keep is None:
        eps_keep = delta * KEEP_MARGIN
    x, cur, ov, cv = K.strictify(x0)
    best = (cur, x.copy()) if (ov <= 1e-11 and cv <= 1e-9
                               and is_blocked_d(x, delta)) else None
    em = None
    nstep = 0
    dtr = delta0
    for _r in range(rounds):
        if dtr < TRUST_MIN:
            break
        y, _sel = sqp_step_d(x, keep_k0, dtr, eps_keep)
        if y is None:
            dtr *= 0.4
            continue
        ws, sg, good, blk = _blocked_feasible_d(y, delta)
        if not good or sg > cur - 1e-12:
            dtr *= 0.4
            continue
        if not blk:
            if em is None:
                em = _exit_record_d(x, y, delta)
            if not keep_k0:
                return x, best, em, nstep
            dtr *= 0.4
            continue
        x = ws; cur = sg; nstep += 1
        if best is None or sg < best[0]:
            best = (sg, ws.copy())
        dtr = min(delta0, dtr * 1.6)
    return x, best, em, nstep


# ================================================================ per-seed driver

def run_seed_d(tag, rng, sub, delta):
    t0 = time.time()
    rec = {'tag': tag, 'delta': delta}
    x0 = None
    for _ in range(40):
        x0 = build_seed_d(rng, sub, delta)
        if x0 is not None:
            break
    if x0 is None:
        rec['status'] = 'seed_failed'
        rec['secs'] = time.time() - t0
        return rec, None
    st0 = k0_state_d(x0, delta)
    rec['sigma_seed'] = K.enclosing_side_x(x0)
    rec['seed_n_block'] = st0['n_block']
    rec['seed_m2'] = [float(v) for v in st0['m2']]

    # flow A: FREE descent, halted at the strict K0-BLOCKED boundary
    _xf, best_free, em, nf = sqp_flow_d(x0, delta, False, ROUNDS_FREE)
    rec['free_exit'] = em
    rec['free_exited'] = bool(em is not None)
    rec['sigma_free_best'] = best_free[0] if best_free else None
    rec['free_steps'] = nf

    # flow B: the same descent CONFINED to K0-BLOCKED(delta)
    xc, best_c, _em2, nc = sqp_flow_d(x0, delta, True, ROUNDS_CONF)
    rec['confined_steps'] = nc
    rec['sigma_confined'] = best_c[0] if best_c else None
    xb = best_c[1] if best_c else xc

    cands = []
    for lbl, bb in (('free', best_free), ('confined', best_c)):
        if bb is not None:
            cands.append((bb[0], lbl, bb[1]))
    cands.sort(key=lambda t: t[0])
    xbest = cands[0][2] if cands else None
    rec['sigma_best_blocked'] = float(cands[0][0]) if cands else None
    rec['best_from'] = cands[0][1] if cands else None
    if xbest is not None:
        st = k0_state_d(xbest, delta)
        rec['blocked_at_best'] = bool(st['blocked'])
        rec['best_n_block'] = st['n_block']
        rec['best_m1'] = [float(v) for v in st['m1']]
        rec['best_m2'] = [float(v) for v in st['m2']]
        ovb, cvb = K.feas(xbest)
        rec['best_ov'] = float(ovb); rec['best_cv'] = float(cvb)
    rec['status'] = 'ok'
    rec['secs'] = time.time() - t0
    return rec, xbest


# ================================================================ exact verify

def verify_record(x, delta):
    """Exact verification: rational z, interval SAT pair/container gaps >= 0,
    certified per-corner meeter counts AT THE FLOOR."""
    z = F.canonical(K.x_to_z(x))
    zi = F.inflate(z)
    xi = K.z_to_x(zi)
    zf = K.zfrac_of(zi)
    ver = F.verify_exact(zf)
    tel = exact_blocked_test_d(zf, delta)
    st = k0_state_d(xi, delta)
    return {
        'sigma_float': float(K.enclosing_side_x(xi)),
        'sigma_inflated': float(F.enclosing_side(zi)),
        'side_upper_bound': ver['side_upper_bound'],
        'disjoint_certified': ver['disjoint_certified'],
        'verify': ver,
        'float_n_block': st['n_block'],
        'float_m1': [float(v) for v in st['m1']],
        'float_m2': [float(v) for v in st['m2']],
        'exact_n_meet': tel['n_meet_certified'],
        'exact_unknown': tel['n_unknown_per_corner'],
        'exact_d1': tel['d1_per_corner'],
        'exact_d2': tel['d2_per_corner'],
        'exact_dps': tel['dps'],
        'K0_BLOCKED_certified': tel['K0_BLOCKED_certified'],
        'below_4': bool(ver['side_upper_bound'] < 4.0),
        'z': [T.frac_str(v) for v in zf]}


# ==================================================================== campaign

def run_floor(delta, nseeds, rng, wall, log, jl):
    t0 = time.time()
    sub = pool_for(delta, rng, log)
    recs = []
    cands = []
    for i in range(nseeds):
        if time.time() - t0 > wall:
            log('  [%.0e] wall cap after %d seeds' % (delta, i))
            break
        tag = 'd%s_s%04d' % (('%.0e' % delta).replace('-', 'm'), i)
        rec, xb = run_seed_d(tag, rng, sub, delta)
        jl.write(json.dumps(rec) + '\n'); jl.flush()
        recs.append(rec)
        if xb is not None and rec.get('sigma_best_blocked') is not None \
                and rec.get('blocked_at_best') and rec['best_ov'] <= 1e-9 \
                and rec['best_cv'] <= 1e-9:
            cands.append((rec['sigma_best_blocked'], tag, xb.copy()))
        if (i + 1) % 50 == 0:
            log('  [%.0e] %4d seeds, %.0fs, best sigma = %s'
                % (delta, i + 1, time.time() - t0,
                   ('%.9f' % min(c[0] for c in cands)) if cands else 'none'))
    log('  [%.0e] descent: %d seeds in %.0fs' % (delta, len(recs), time.time() - t0))

    # ---- deep re-run: walk the pinned depth DOWN onto the floor
    cands.sort(key=lambda c: c[0])
    ladder_mults = (4.0, 2.0, 1.3, KEEP_MARGIN)
    deep = []
    for sg, tag, xb in cands[:DEEP_N]:
        if time.time() - t0 > wall + 900:
            log('  [%.0e] deep cap' % delta); break
        xcur = xb
        best_d = None
        lad = []
        for mult in ladder_mults:
            eps = delta * mult
            _xd, bd, _emd, nd = sqp_flow_d(xcur, delta, True, ROUNDS_DEEP,
                                           eps_keep=eps, delta0=0.04)
            if bd is None:
                break
            best_d = bd; xcur = bd[1]
            lad.append({'eps': eps, 'sigma': float(bd[0]), 'steps': nd})
        if best_d is None:
            continue
        sgd, xdb = best_d
        st = k0_state_d(xdb, delta)
        d = {'delta': delta, 'tag': tag, 'sigma_in': sg, 'sigma_deep': float(sgd),
             'deep_steps': sum(r['steps'] for r in lad), 'eps_ladder': lad,
             'n_block': st['n_block'],
             'm1': [float(v) for v in st['m1']],
             'm2': [float(v) for v in st['m2']]}
        deep.append((float(sgd), tag, xdb.copy(), d))
        log('  [%.0e] deep %s %.7f -> %.9f  n_block %s  m2 %s'
            % (delta, tag, sg, sgd, st['n_block'],
               ' '.join('%.2e' % v for v in st['m2'])))
    deep.sort(key=lambda t: t[0])

    # ---- exact verification of the lowest endpoints
    pool_v = [(d[0], d[1], d[2]) for d in deep] + cands
    seen = set(); ordered = []
    for sg, tag, xx in sorted(pool_v, key=lambda t: t[0]):
        k = (tag, round(sg, 10))
        if k in seen:
            continue
        seen.add(k); ordered.append((sg, tag, xx))
    verified = []
    for sg, tag, xx in ordered[:VERIFY_N]:
        try:
            v = verify_record(xx, delta)
        except Exception as ex:
            log('  [%.0e] verify %s FAILED %s' % (delta, tag, repr(ex)[:120]))
            continue
        v['tag'] = tag; v['sigma_in'] = float(sg); v['delta'] = delta
        verified.append(v)
        log('  [%.0e] verify %s: side_upper %.12f  exact n_meet %s  unknown %s  '
            'disjoint %s  BLOCKED %s'
            % (delta, tag, v['side_upper_bound'], v['exact_n_meet'],
               v['exact_unknown'], v['disjoint_certified'],
               v['K0_BLOCKED_certified']))
    good = [v for v in verified
            if v['K0_BLOCKED_certified'] and v['disjoint_certified']]
    good.sort(key=lambda v: v['side_upper_bound'])

    ok = [r for r in recs if r.get('status') == 'ok']
    sbb = [r['sigma_best_blocked'] for r in ok
           if r.get('sigma_best_blocked') is not None and r.get('blocked_at_best')]
    ex_sig = sorted(r['free_exit']['sigma_exit'] for r in ok if r.get('free_exit'))
    modes = {}; freed = {}
    for r in ok:
        e = r.get('free_exit')
        if not e:
            continue
        for m in e['modes']:
            modes[m['mode']] = modes.get(m['mode'], 0) + 1
            freed[m['corner']] = freed.get(m['corner'], 0) + 1
    return {
        'delta': delta,
        'n_pairs_in_pool': len(sub),
        'n_seeds_attempted': len(recs),
        'n_seeds_built': len(ok),
        'n_seed_failed': sum(1 for r in recs if r.get('status') == 'seed_failed'),
        'n_free_exited': len(ex_sig),
        'free_exit_sigma': {
            'min': ex_sig[0] if ex_sig else None,
            'p10': ex_sig[len(ex_sig) // 10] if ex_sig else None,
            'median': ex_sig[len(ex_sig) // 2] if ex_sig else None,
            'p90': ex_sig[9 * len(ex_sig) // 10] if ex_sig else None,
            'max': ex_sig[-1] if ex_sig else None,
            'n_below_4': sum(1 for v in ex_sig if v < 4.0)},
        'exit_modes': modes, 'exit_corner': freed,
        'sigma_best_blocked': {
            'min': min(sbb) if sbb else None,
            'p10': sorted(sbb)[len(sbb) // 10] if sbb else None,
            'median': sorted(sbb)[len(sbb) // 2] if sbb else None,
            'n': len(sbb),
            'n_below_4': sum(1 for v in sbb if v < 4.0),
            'frac_below_4': (sum(1 for v in sbb if v < 4.0) / len(sbb))
            if sbb else None},
        'n_deep': len(deep),
        'deep_min_sigma': deep[0][0] if deep else None,
        'deep_rows': [d[3] for d in deep],
        'n_verified': len(verified),
        'n_verified_blocked': len(good),
        'lowest_verified_side': good[0]['side_upper_bound'] if good else None,
        'record': good[0] if good else None,
        'verified': verified,
        'secs': time.time() - t0}


def canary(log=print):
    """Trump must be K0-FREE at EVERY floor (BL/BR/TR hold exactly one square) and
    its TL 2-crowd depths 0.168 / 0.155 must clear the 1e-2 floor."""
    ok = True
    x = K.trump_x()
    log('canary: Trump s = %.12f' % K.enclosing_side_x(x))
    zf = K.zfrac_of(F.canonical(K.x_to_z(x)))
    out = {}
    for delta in FLOORS:
        st = k0_state_d(x, delta)
        tel = exact_blocked_test_d(zf, delta)
        nb = st['n_block']; ex = tel['n_meet_certified']
        log('   floor %.0e: float n_block %s  exact certified %s  unknown %s  '
            'blocked %s  TL depths %.6f/%.6f'
            % (delta, nb, ex, tel['n_unknown_per_corner'], st['blocked'],
               st['m1'][CORNERS.index('TL')], st['m2'][CORNERS.index('TL')]))
        if nb != [1, 1, 2, 1]:
            log('   FAIL float n_block %s != [1,1,2,1] at %.0e' % (nb, delta)); ok = False
        if ex != [1, 1, 2, 1]:
            log('   FAIL exact n_meet %s != [1,1,2,1] at %.0e' % (ex, delta)); ok = False
        if st['blocked'] or tel['K0_BLOCKED_certified']:
            log('   FAIL Trump reported K0-BLOCKED at %.0e' % delta); ok = False
        out['%.0e' % delta] = {'float_n_block': nb, 'exact_n_meet': ex,
                               'blocked': bool(st['blocked']),
                               'TL_depths': [float(st['m1'][CORNERS.index('TL')]),
                                             float(st['m2'][CORNERS.index('TL')])]}
    kTL = CORNERS.index('TL')
    st = k0_state_d(x, 1e-2)
    d = sorted([st['m1'][kTL], st['m2'][kTL]], reverse=True)
    if not (abs(d[0] - 0.168) < 6e-3 and abs(d[1] - 0.155) < 6e-3):
        log('   FAIL TL crowd depths %.6f/%.6f, expected ~0.168/0.155' % (d[0], d[1]))
        ok = False
    else:
        log('   TL crowd depths %.6f / %.6f pass the 1e-2 floor  OK' % (d[0], d[1]))
    log('canary: %s' % ('PASS' if ok else 'FAIL'))
    out['pass'] = ok
    out['TL_depths'] = [float(d[0]), float(d[1])]
    return ok, out


def selftest(log=print):
    ok = True
    if not K.selftest(log):
        log('FAIL: inherited k0dir87 selftest'); ok = False
    rng = random.Random(4242)
    # 1. the strict count is monotone non-increasing in the floor
    P = base_pool(rng, n=300, log=log)
    sub = [(a, b) for (a, b, d) in P if d >= 2e-2]
    x = None
    for _ in range(40):
        x = build_seed_d(rng, sub, 1e-2)
        if x is not None:
            break
    if x is None:
        log('FAIL: could not build a 1e-2 seed'); ok = False
    else:
        prev = None
        for delta in (1e-9, 1e-6, 1e-4, 1e-3, 1e-2, 5e-2):
            nb = k0_state_d(x, delta)['n_block']
            if prev is not None and any(a > b for a, b in zip(nb, prev)):
                log('FAIL: n_block not monotone in delta (%s > %s)' % (nb, prev))
                ok = False
            prev = nb
        log('selftest: strict n_block monotone in the floor OK (%s at 1e-2)'
            % k0_state_d(x, 1e-2)['n_block'])
        # 2. exact certified count never exceeds the float count, and matches
        #    when no row is UNKNOWN
        zf = K.zfrac_of(F.canonical(K.x_to_z(x)))
        for delta in (1e-6, 1e-4, 1e-2):
            tel = exact_blocked_test_d(zf, delta)
            fl = k0_state_d(K.z_to_x(np.array([float(v) for v in zf])), delta)['n_block']
            ex = tel['n_meet_certified']
            log('selftest: floor %.0e exact %s (unknown %s) vs float %s'
                % (delta, ex, tel['n_unknown_per_corner'], fl))
            if any(e > f for e, f in zip(ex, fl)) and tel['n_unknown'] == 0:
                log('FAIL: certified count exceeds the float count with no UNKNOWN')
                ok = False
        # 3. a seed built at floor 1e-2 is K0-BLOCKED at every SMALLER floor
        for delta in FLOORS:
            if not is_blocked_d(x, delta):
                log('FAIL: 1e-2 seed not blocked at %.0e' % delta); ok = False
        log('selftest: 1e-2 seed blocked at every floor OK')
    log('selftest: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def run(nseeds=300, wall_per_floor=2400.0, seed=20260905, log=print):
    rng = random.Random(seed)
    t0 = time.time()
    per = {}
    with open(OUT_JL, 'w') as jl:
        for delta in FLOORS:
            log('=== floor delta = %.0e ===' % delta)
            per['%.0e' % delta] = run_floor(delta, nseeds, rng, wall_per_floor, log, jl)
            log('=== floor %.0e done: lowest verified side %s, frac below 4.0 = %s'
                % (delta,
                   ('%.12f' % per['%.0e' % delta]['lowest_verified_side'])
                   if per['%.0e' % delta]['lowest_verified_side'] is not None else 'none',
                   per['%.0e' % delta]['sigma_best_blocked']['frac_below_4']))
    with open(OUT_DEEP, 'w') as fh:
        for k, v in per.items():
            for d in v['deep_rows']:
                fh.write(json.dumps(d) + '\n')
    recs = {k: v.get('record') for k, v in per.items()}
    json.dump(recs, open(OUT_REC, 'w'), indent=1)
    summ = {'attempt': 'A87 chore k0dir2_87: strict-convention directed '
                       'K0-BLOCKED search, depth floor as a hypothesis',
            'floors': list(FLOORS), 'nseeds_per_floor': nseeds,
            'keep_margin': KEEP_MARGIN, 'pool_margin': POOL_MARGIN,
            's_hat': S_HAT, 's0': S0F,
            'secs': time.time() - t0, 'per_floor': per}
    return summ


def write_md(s):
    L = []
    L.append('# k0dir2_87 -- strict-convention directed K0-BLOCKED search\n')
    L.append('*A87 chore. Code `code/k0dir2_87.py`; results `results/k0dir2_87.*`.'
             '  One process, `OMP_NUM_THREADS=1`, %.0f s wall.*\n' % s.get('secs', 0))
    L.append('The depth floor is a **hypothesis**, not an artefact: '
             'K0-BLOCKED(delta) means every one of the four closed unit corner '
             'slots is met by >= 2 squares at CERTIFIED intrusion depth >= delta.\n')
    L.append('## Headline: lowest exact-verified strictly K0-BLOCKED side per floor\n')
    L.append('| delta | lowest verified side | below 4? | exact n_meet | '
             'certified 2nd depths (BL BR TL TR) | frac of flows below 4.0 |')
    L.append('| ---: | ---: | :--: | --- | --- | ---: |')
    for k in ('%.0e' % d for d in s['floors']):
        f = s['per_floor'][k]
        r = f.get('record')
        lv = f.get('lowest_verified_side')
        fb = f['sigma_best_blocked']['frac_below_4']
        L.append('| %s | %s | %s | %s | %s | %s |'
                 % (k,
                    ('%.12f' % lv) if lv is not None else 'none verified',
                    ('YES' if (lv is not None and lv < 4.0) else 'no'),
                    r['exact_n_meet'] if r else '-',
                    (' '.join(('%.3e' % v) if v is not None else '-'
                              for v in r['exact_d2'])) if r else '-',
                    ('%.4f' % fb) if fb is not None else '-'))
    L.append('')
    L.append('## Free flows (no constraint): exit side under the strict convention\n')
    L.append('The side at which some corner drops below 2 strict meeters.\n')
    L.append('| delta | n flows | min | p10 | median | p90 | max | n exits below 4.0 |')
    L.append('| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    for k in ('%.0e' % d for d in s['floors']):
        e = s['per_floor'][k]['free_exit_sigma']
        L.append('| %s | %d | %s | %s | %s | %s | %s | %d |'
                 % (k, s['per_floor'][k]['n_free_exited'],
                    *[('%.9f' % e[q]) if e[q] is not None else '-'
                      for q in ('min', 'p10', 'median', 'p90', 'max')],
                    e['n_below_4']))
    L.append('')
    L.append('## Constrained flows: lowest K0-BLOCKED side reached per seed\n')
    L.append('| delta | n | min | p10 | median | n below 4.0 | frac below 4.0 |')
    L.append('| ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    for k in ('%.0e' % d for d in s['floors']):
        b = s['per_floor'][k]['sigma_best_blocked']
        L.append('| %s | %d | %s | %s | %s | %d | %s |'
                 % (k, b['n'],
                    *[('%.9f' % b[q]) if b[q] is not None else '-'
                      for q in ('min', 'p10', 'median')],
                    b['n_below_4'],
                    ('%.4f' % b['frac_below_4']) if b['frac_below_4'] is not None
                    else '-'))
    L.append('')
    L.append('## Record per floor (corner depths)\n')
    for k in ('%.0e' % d for d in s['floors']):
        f = s['per_floor'][k]
        r = f.get('record')
        L.append('### delta = %s' % k)
        if not r:
            L.append('\nNo endpoint verified as strictly K0-BLOCKED.\n')
            continue
        L.append('')
        L.append('* tag `%s`, certified side upper bound **%.12f**, '
                 'pair-disjointness certified %s, interval dps %s.'
                 % (r['tag'], r['side_upper_bound'], r['disjoint_certified'],
                    r['exact_dps']))
        L.append('* exact certified meeter counts (BL BR TL TR) = %s, UNKNOWN = %s.'
                 % (r['exact_n_meet'], r['exact_unknown']))
        L.append('')
        L.append('| corner | certified deepest | certified 2nd | float deepest | float 2nd |')
        L.append('| --- | ---: | ---: | ---: | ---: |')
        for i, cn in enumerate(CORNERS):
            L.append('| %s | %s | %s | %.6e | %.6e |'
                     % (cn,
                        ('%.6e' % r['exact_d1'][i]) if r['exact_d1'][i] is not None else '-',
                        ('%.6e' % r['exact_d2'][i]) if r['exact_d2'][i] is not None else '-',
                        r['float_m1'][i], r['float_m2'][i]))
        L.append('')
    L.append('## Exit modes / corner freed\n')
    L.append('| delta | modes | corners freed |')
    L.append('| --- | --- | --- |')
    for k in ('%.0e' % d for d in s['floors']):
        f = s['per_floor'][k]
        L.append('| %s | %s | %s |' % (k, f['exit_modes'], f['exit_corner']))
    L.append('')
    L.append('## Counts\n')
    L.append('| delta | pool pairs | seeds attempted | built | failed | deep | '
             'verified | verified BLOCKED | secs |')
    L.append('| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    for k in ('%.0e' % d for d in s['floors']):
        f = s['per_floor'][k]
        L.append('| %s | %d | %d | %d | %d | %d | %d | %d | %.0f |'
                 % (k, f['n_pairs_in_pool'], f['n_seeds_attempted'],
                    f['n_seeds_built'], f['n_seed_failed'], f['n_deep'],
                    f['n_verified'], f['n_verified_blocked'], f['secs']))
    L.append('')
    c = s.get('canary')
    if c:
        L.append('## Canary\n')
        L.append('Trump must be K0-FREE at every floor (3 slot corners hold exactly '
                 'one square) and its TL crowd depths must clear 1e-2.\n')
        L.append('| delta | float n_block | exact certified n_meet | K0-BLOCKED? |')
        L.append('| ---: | --- | --- | :--: |')
        for k in ('%.0e' % d for d in s['floors']):
            e = c.get(k, {})
            L.append('| %s | %s | %s | %s |'
                     % (k, e.get('float_n_block'), e.get('exact_n_meet'),
                        e.get('blocked')))
        L.append('')
        L.append('TL crowd depths %.6f / %.6f -- both above 1e-2.  Canary %s.\n'
                 % (c['TL_depths'][0], c['TL_depths'][1],
                    'PASS' if c.get('pass') else 'FAIL'))
    L.append('## Conventions and caveats\n')
    L.append('* Acceptance is judged by the strict test **at the floor** on the '
             'strictified (`fjpolish87.inflate`) iterate, so every point counted '
             'K0-BLOCKED is a genuine packing.')
    L.append('* The confined SQP pins the two deepest intruders per corner to '
             'depth >= %.2f*delta so that the strictify step cannot push an '
             'accepted iterate back below the floor.  Reported sides are '
             'therefore UPPER bounds on the true infimum at each floor.'
             % KEEP_MARGIN)
    L.append('* The exact test uses the sound INNER slot of k0dir87 (a rational '
             'rectangle contained in the true unit slot for every realisation of '
             'the interval bounding box), with the bar at the floor: MEETS iff '
             '`gap.b <= -delta`, does NOT meet iff `gap.a > -delta`.')
    L.append('* This is a numerical SEARCH, not a proof of non-existence.\n')
    open(OUT_MD, 'w').write('\n'.join(L) + '\n')


def export_records(s):
    """results/k0dir2_87.records.json -- per floor, the lowest exact-verified
    strictly K0-BLOCKED packing in DRAWABLE form: the 11 exact poses as
    (cx, cy, tilt_deg) (rational strings plus floats), the certified side, the
    per-corner certified meeter counts and the certified 1st/2nd meeter depths."""
    out = {'attempt': 'A87 chore k0dir2_87 records',
           's_hat': S_HAT, 's0': S0F,
           'convention': 'MEETS iff certified intrusion depth >= delta; '
                         'K0-BLOCKED(delta) iff every corner slot has >= 2 meeters',
           'floors': {}}
    for d in s['floors']:
        k = '%.0e' % d
        r = s['per_floor'][k].get('record')
        if not r:
            out['floors'][k] = {'delta': d, 'record': None,
                                'note': 'no endpoint verified strictly K0-BLOCKED'}
            continue
        zf = [Fraction(v) for v in r['z']]
        poses = []
        for j in range(11):
            cx, cy, th = zf[3 * j], zf[3 * j + 1], zf[3 * j + 2]
            poses.append({
                'i': j,
                'cx': float(cx), 'cy': float(cy),
                'tilt_deg': math.degrees(float(th)),
                'theta_rad': float(th),
                'cx_exact': str(cx), 'cy_exact': str(cy),
                'theta_exact': str(th)})
        side_f = zf[33]
        # is every corner blocked only by FLOOR-DEPTH second meeters?
        d2 = r['exact_d2']
        at_floor = [(v is not None and v < 10.0 * d) for v in d2]
        out['floors'][k] = {
            'delta': d,
            'tag': r['tag'],
            'certified_side_upper_bound': r['side_upper_bound'],
            'side_float': r['sigma_inflated'],
            'container_side_exact': str(side_f),
            'below_4': bool(r['side_upper_bound'] < 4.0),
            'disjoint_certified': r['disjoint_certified'],
            'interval_dps': r['exact_dps'],
            'corners': CORNERS,
            'n_meet_certified': r['exact_n_meet'],
            'n_unknown': r['exact_unknown'],
            'depth_first_meeter': r['exact_d1'],
            'depth_second_meeter': r['exact_d2'],
            'second_meeters_within_10x_floor': at_floor,
            'all_corners_at_floor_only': bool(all(at_floor)),
            'poses': poses,
            'verify': r['verify']}
    json.dump(out, open(OUT_REC, 'w'), indent=1)
    return out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'records':
        export_records(json.load(open(OUT_JS)))
        print('wrote %s' % OUT_REC)
    elif cmd == 'selftest':
        sys.exit(0 if selftest() else 1)
    elif cmd == 'canary':
        ok, _ = canary()
        sys.exit(0 if ok else 1)
    elif cmd == 'report':
        write_md(json.load(open(OUT_JS)))
    elif cmd == 'run':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        w = float(sys.argv[3]) if len(sys.argv) > 3 else 2400.0
        lf = open(os.path.join(LOGS, 'k0dir2_87.log'), 'w', buffering=1)

        def log(*a):
            m = ' '.join(str(v) for v in a)
            lf.write(m + '\n'); lf.flush()
            print(m, flush=True)
        ok1 = selftest(log)
        ok2, cn = canary(log)
        if not (ok1 and ok2):
            log('SELFTEST/CANARY FAILED -- not running the campaign')
            sys.exit(1)
        s = run(n, wall_per_floor=w, log=log)
        s['canary'] = cn
        json.dump(s, open(OUT_JS, 'w'), indent=1)
        write_md(s)
        log('DONE')
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
