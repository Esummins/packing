"""A90 / T3 -- empirical checks for Theorem NOCRIT (K0-BLOCKED has no FJ point).

Implements the theory lead's definitions verbatim:

  * corner frame  = the D4 map sending corner c of the TIGHT BOUNDING BOX to the
    origin with the packing in the positive quadrant (the same anchors k0dir87's
    k0_state / k0blocked87's exact_blocked_test use, so "intruder" here is the
    same predicate as "blocker" there);
  * depth      d_c(Q) = max(0, 1 - min_{p in Q} max(p_x, p_y))   in c's frame;
  * argmin set A(Q), retreat cone K(Q), cardinal retreat directions e_x, e_y;
  * active contacts (walls + pairs, SAT gap <= 1e-6) with the force normal ON Q;
  * blocking contact / cluster C_e(Q) / wall-anchored / intruder-anchored;
  * RETREATABLE(Q), RES(z);
  * Lemma LOCK (b) LP and the Lemma MENU far-side test.

Everything geometric is float (k0dir87 / fjpolish87 conventions); the K0-BLOCKED
verdicts quoted in the report are the EXACT interval ones of
k0dir87.exact_blocked_test, and the FJ machinery is fjpolish87's.

No A87/A89 file is modified: this module imports them.

Usage:  python t3_90.py {check3|task1 [N]|task2|task3|task4 [N]}
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json
import math
import random
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
A90 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A90, '..'))
A87 = os.path.join(ATT, 'A87-drain-flow')
A85 = os.path.join(ATT, 'A85-k0-route')
sys.path.insert(0, os.path.join(A87, 'code'))
sys.path.insert(0, os.path.join(A85, 'code'))

import cp85                     # noqa: E402
import k0dir87 as KD            # noqa: E402
import k0blocked87 as KB        # noqa: E402
import fjpolish87 as F          # noqa: E402
import t3lib as T               # noqa: E402

RESULTS = os.path.join(A90, 'results')
NOTES = os.path.join(A90, 'notes')
LOGS = os.path.join(A90, 'logs')
for _d in (RESULTS, NOTES, LOGS):
    os.makedirs(_d, exist_ok=True)

N = 11
H = 0.5
HALFPI = math.pi / 2.0
CORNERS = ('BL', 'BR', 'TL', 'TR')
# corner frame: (ox, oy, sx, sy);  p_frame = (sx*(p_x-ox), sy*(p_y-oy))
FSGN = {'BL': (1.0, 1.0), 'BR': (-1.0, 1.0), 'TL': (1.0, -1.0), 'TR': (-1.0, -1.0)}

TOL_BLOCK = 1e-9          # a tangency is NOT a block (k0dir87's floor)
TOL_CONTACT = 1e-6        # active contact
TOL_PT = 1e-6             # a vertex counts as a contact point
TOL_AXIS = 1e-6           # an axis counts as admissible (corner-corner kiss)
TOL_ARG = 1e-11           # argmin set tolerance
TOL_SIGN = 1e-11          # p*_x vs p*_y comparison
TOL_DIR = 1e-12           # v_x > 0 test


# ===================================================================== geometry

def verts(c, th):
    """4x2 vertices of the unit square (c, th), ccw."""
    ct, st = math.cos(th), math.sin(th)
    u = np.array([ct, st]) * H
    v = np.array([-st, ct]) * H
    return np.array([c + u + v, c + u - v, c - u - v, c - u + v])


def all_verts(C, TH):
    return np.array([verts(C[i], TH[i]) for i in range(len(TH))])


def tight_bbox_of(C, TH):
    q = all_verts(C, TH).reshape(-1, 2)
    return float(q[:, 0].min()), float(q[:, 0].max()), \
        float(q[:, 1].min()), float(q[:, 1].max())


def frame(bbox, cn):
    xlo, xhi, ylo, yhi = bbox
    sx, sy = FSGN[cn]
    ox = xlo if sx > 0 else xhi
    oy = ylo if sy > 0 else yhi
    return (ox, oy, sx, sy)


def to_frame(P, fr):
    ox, oy, sx, sy = fr
    P = np.atleast_2d(P)
    return np.stack([sx * (P[:, 0] - ox), sy * (P[:, 1] - oy)], axis=1)


def vec_to_frame(v, fr):
    _ox, _oy, sx, sy = fr
    return np.array([sx * v[0], sy * v[1]])


def vec_to_world(v, fr):
    _ox, _oy, sx, sy = fr
    return np.array([sx * v[0], sy * v[1]])       # involutive


def _fval(p):
    return max(p[0], p[1])


def depth_arg(V, fr):
    """(depth, fmin, argmin points in c's frame) for a square with world
    vertices V (4x2).  f(p) = max(p_x, p_y) is convex piecewise linear, so its
    minimum over the quadrilateral is attained at a vertex or where an edge meets
    the diagonal {p_x = p_y}."""
    W = to_frame(V, fr)
    cand = [W[k] for k in range(4)]
    for k in range(4):
        a, b = W[k], W[(k + 1) % 4]
        d = (b[0] - a[0]) - (b[1] - a[1])
        if abs(d) > 1e-14:
            t = (a[1] - a[0]) / d
            if -1e-12 <= t <= 1 + 1e-12:
                t = min(1.0, max(0.0, t))
                cand.append(a + t * (b - a))
    vals = [_fval(p) for p in cand]
    fmin = min(vals)
    A = []
    for p, v in zip(cand, vals):
        if v <= fmin + TOL_ARG:
            if not any(np.max(np.abs(p - q)) < 1e-12 for q in A):
                A.append(p)
    return max(0.0, 1.0 - fmin), fmin, A


def f_rate(A, v):
    """min over p* in A of the one-sided derivative of f at p* along v."""
    r = []
    for p in A:
        if p[0] < p[1] - TOL_SIGN:
            r.append(v[1])
        elif p[0] > p[1] + TOL_SIGN:
            r.append(v[0])
        else:
            r.append(max(v[0], v[1]))
    return min(r) if r else 0.0


def in_K(A, v):
    """v (in c's frame) is in the retreat cone K(Q): depth strictly decreasing."""
    return f_rate(A, v) > TOL_DIR


def corner_state(C, TH, bbox):
    """Per corner: depths of all 11 squares, intruders, deepest, argmin sets."""
    V = all_verts(C, TH)
    out = {}
    for cn in CORNERS:
        fr = frame(bbox, cn)
        dep, args = [], []
        for i in range(len(TH)):
            d, _f, A = depth_arg(V[i], fr)
            dep.append(d)
            args.append(A)
        dep = np.array(dep)
        intr = [i for i in range(len(TH)) if dep[i] > TOL_BLOCK]
        dmax = max((dep[i] for i in intr), default=0.0)
        out[cn] = {'frame': fr, 'depth': dep, 'intruders': intr,
                   'args': args, 'dmax': float(dmax),
                   'n_block': len(intr)}
    return out


# --------------------------------------------------------------- contacts

def pair_contact(C, TH, i, j):
    """SAT contact data between squares i and j (None if gap > TOL_CONTACT)."""
    q = {i: verts(C[i], TH[i]), j: verts(C[j], TH[j])}
    best = None
    axes = []
    amap = {}
    for o, p in ((i, j), (j, i)):
        for e in range(4):
            a = TH[o] + e * HALFPI
            n = np.array([math.cos(a), math.sin(a)])
            proj = q[p] @ n
            val = float(proj.min() - C[o] @ n - H)
            axes.append((val, o, p, e, n, proj))
            amap[(int(o), int(p), int(e))] = n
            if best is None or val > best[0]:
                best = (val, o, p, e, n, proj)
    gap = best[0]
    if gap > TOL_CONTACT:
        return None
    adm = [(o, p, e) for (val, o, p, e, _n, _pr) in axes if val >= gap - TOL_AXIS]
    val, o, p, e, n, proj = best
    pts = [q[p][k] for k in range(4) if proj[k] <= proj.min() + TOL_PT]
    if len(adm) > 1:
        kind = 'kiss'
    elif len(pts) >= 2:
        kind = 'flush'
    else:
        kind = 'vertex'
    return {'i': i, 'j': j, 'gap': gap, 'owner': o, 'other': p, 'e': e,
            'n': n, 'pts': pts, 'kind': kind, 'n_admissible': len(adm),
            'admissible': [(int(a), int(b), int(c)) for a, b, c in adm],
            '_axes': amap}


def all_pair_contacts(C, TH):
    out = []
    for i in range(len(TH)):
        for j in range(i + 1, len(TH)):
            ct = pair_contact(C, TH, i, j)
            if ct is not None:
                out.append(ct)
    return out


WALLN = {'x=0': np.array([1.0, 0.0]), 'y=0': np.array([0.0, 1.0]),
         'x=s': np.array([-1.0, 0.0]), 'y=s': np.array([0.0, -1.0])}


def wall_contacts(C, TH, s):
    """Container walls of [0,s]^2.  Also reported: which tight-bbox face."""
    out = []
    V = all_verts(C, TH)
    for i in range(len(TH)):
        for k in range(4):
            x, y = V[i][k]
            for w, g in (('x=0', x), ('y=0', y), ('x=s', s - x), ('y=s', s - y)):
                if g <= TOL_CONTACT:
                    out.append({'i': i, 'wall': w, 'gap': float(g),
                                'n': WALLN[w], 'pt': V[i][k], 'k': k})
    return out


def contacts_on(Q, pcs, wcs):
    """Active rows of square Q as (n_on_Q, contact point, label) triples."""
    rows = []
    for ct in pcs:
        if Q not in (ct['i'], ct['j']):
            continue
        other = ct['j'] if ct['i'] == Q else ct['i']
        nQ = ct['n'] if ct['other'] == Q else -ct['n']
        for pt in ct['pts']:
            rows.append({'kind': 'pair', 'other': int(other), 'n': nQ,
                         'pt': np.asarray(pt, float), 'gap': ct['gap'],
                         'type': ct['kind'], 'n_admissible': ct['n_admissible'],
                         'admissible': ct['admissible']})
    for wc in wcs:
        if wc['i'] != Q:
            continue
        rows.append({'kind': 'wall', 'other': wc['wall'], 'n': wc['n'],
                     'pt': np.asarray(wc['pt'], float), 'gap': wc['gap'],
                     'type': 'wall', 'n_admissible': 1, 'admissible': []})
    return rows


# --------------------------------------------------------------- clusters

def cluster(Q, e_world, pcs, tol=0.0):
    """C_e(Q): closure of {Q} under 'N has a blocking contact with a member'.

    A pair contact of member M with outsider N is BLOCKING iff n_M . e < 0.
    For a corner-corner kiss the contact counts as blocking only if EVERY
    admissible axis gives n_M . e < 0."""
    mem = {Q}
    edges = []
    changed = True
    while changed:
        changed = False
        for ct in pcs:
            for M, Nn in ((ct['i'], ct['j']), (ct['j'], ct['i'])):
                if M not in mem or Nn in mem:
                    continue
                if _blocking(ct, M, e_world, tol):
                    mem.add(Nn)
                    edges.append((int(M), int(Nn)))
                    changed = True
    return sorted(int(v) for v in mem), edges


def _blocking(ct, M, e, tol):
    """n_M . e < 0 (all admissible axes for a kiss)."""
    if ct['n_admissible'] <= 1:
        nM = ct['n'] if ct['other'] == M else -ct['n']
        return float(nM @ e) < -tol
    # kiss: every admissible axis must block
    ok = True
    for (o, p, ee) in ct['admissible']:
        n = ct['_axes'][(int(o), int(p), int(ee))]
        nM = n if p == M else -n
        ok = ok and float(nM @ e) < -tol
    return ok


def wall_anchored(members, e_world, wcs):
    """Some member touches a wall whose inward normal opposes e."""
    hits = []
    for wc in wcs:
        if wc['i'] in members and float(wc['n'] @ e_world) < -1e-12:
            hits.append((int(wc['i']), wc['wall']))
    return (len(hits) > 0), hits


def intruder_anchored(members, e_world, cst, home_corner, C, TH, bbox):
    """A member is an intruder at another corner whose depth STRICTLY INCREASES
    under translation by e (first order); cross-checked by finite difference."""
    hits = []
    V = all_verts(C, TH)
    for M in members:
        for cn in CORNERS:
            if cn == home_corner:
                continue
            d = float(cst[cn]['depth'][M])
            if d <= TOL_BLOCK:
                continue
            fr = cst[cn]['frame']
            A = cst[cn]['args'][M]
            ef = vec_to_frame(e_world, fr)
            rate = -f_rate(A, ef)            # d(depth)/dt
            h = 1e-7
            d2, _f, _A = depth_arg(V[M] + h * e_world[None, :], fr)
            fd = (d2 - d) / h
            if rate > 1e-9:
                hits.append({'sq': int(M), 'corner': cn, 'depth': d,
                             'rate': float(rate), 'fd': float(fd)})
    return (len(hits) > 0), hits


# --------------------------------------------------------------- LOCK / MENU

def tilt_of(th):
    d = math.fmod(th, HALFPI)
    if d < 0:
        d += HALFPI
    return d if d <= HALFPI / 2 else HALFPI - d


def signed_tilt(th):
    """delta' in (-45, 45] degrees (radians): th mod 90 mapped into (-45,45]."""
    d = math.fmod(th, HALFPI)
    if d > HALFPI / 2:
        d -= HALFPI
    if d <= -HALFPI / 2:
        d += HALFPI
    return d


def lock_lp(rows, cQ):
    """Lemma LOCK (b): exists mu >= 0 nonzero with sum mu_k (n_k, tau_k) =
    (0, nu) and nu in the given rotation sense.  Returns per-sense verdicts."""
    m = len(rows)
    if m == 0:
        return {'m': 0, 'plus': False, 'minus': False, 'selfstress': False}
    Nn = np.array([r['n'] for r in rows])
    tau = np.array([float((r['pt'][0] - cQ[0]) * r['n'][1]
                          - (r['pt'][1] - cQ[1]) * r['n'][0]) for r in rows])
    out = {'m': m}
    for lbl, sg in (('plus', 1.0), ('minus', -1.0)):
        A_eq = Nn.T                        # 2 x m
        b_eq = np.zeros(2)
        A_ub = (-sg * tau)[None, :]        # -sg*sum mu tau <= 0  <=>  sg*nu >= 0
        b_ub = np.zeros(1)
        r = linprog(-np.ones(m), A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                    bounds=[(0, 1)] * m, method='highs')
        out[lbl] = bool(r.success and -r.fun > 1e-9)
        out[lbl + '_mass'] = float(-r.fun) if r.success else 0.0
    # pure self-stress: sum mu n = 0 and sum mu tau = 0
    r = linprog(-np.ones(m), A_eq=np.vstack([Nn.T, tau[None, :]]),
                b_eq=np.zeros(3), bounds=[(0, 1)] * m, method='highs')
    out['selfstress'] = bool(r.success and -r.fun > 1e-9)
    return out


def menu_status(Q, C, TH, rows, wcs):
    """Lemma MENU: a wall-touching blocker at tilt delta is flush-locked only if
    it has an active FAR-SIDE contact.  Far-side is computed as the general rate
    test of the MENU table: rotate Q about the wall-contact vertex O in the
    flush-ward sense; a contact CLOSES (rate < 0) iff it is far-side."""
    th = TH[Q]
    dl = signed_tilt(th)
    tilt = abs(dl)
    if tilt < 1e-9:
        return {'applies': False, 'reason': 'flush', 'tilt': tilt}
    my_walls = [wc for wc in wcs if wc['i'] == Q]
    if not my_walls:
        return {'applies': False, 'reason': 'no_wall_contact', 'tilt': tilt}
    senses = [-math.copysign(1.0, dl)]
    if abs(tilt - HALFPI / 2) < 1e-9:
        senses = [1.0, -1.0]
    piv = []
    for wc in my_walls:
        O = wc['pt']
        for om in senses:
            far = []
            for k, r in enumerate(rows):
                # velocity of the contact point under rotation about O
                d = r['pt'] - O
                u = om * np.array([-d[1], d[0]])
                rate = float(r['n'] @ u)
                if rate < -1e-9:
                    far.append({'k': k, 'kind': r['kind'],
                                'other': r['other'], 'rate': rate})
            piv.append({'wall': wc['wall'], 'O': [float(v) for v in O],
                        'omega': float(om), 'n_far': len(far), 'far': far})
    locked = all(p['n_far'] > 0 for p in piv)
    return {'applies': True, 'tilt': float(tilt), 'pivots': piv,
            'MENU_LOCKED': bool(locked)}


# --------------------------------------------------------- the T3 predicates

def analyse_square(Q, cn, C, TH, s, bbox, cst, pcs, wcs, want_clusters=True):
    """Full T3 report on square Q as an intruder at corner cn."""
    fr = cst[cn]['frame']
    dep = cst[cn]['depth']
    A = cst[cn]['args'][Q]
    d = float(dep[Q])
    others = [float(dep[i]) for i in cst[cn]['intruders'] if i != Q]
    non_deepest = bool(others and max(others) >= d - 0.0)
    K = {}
    for lbl, v in (('e_x', np.array([1.0, 0.0])), ('e_y', np.array([0.0, 1.0])),
                   ('(1,1)', np.array([1.0, 1.0]))):
        K[lbl] = bool(in_K(A, v))
    cards = [lbl for lbl in ('e_x', 'e_y') if K[lbl]]
    rows = contacts_on(Q, pcs, wcs)
    out = {
        'sq': int(Q), 'corner': cn, 'depth': d, 'tilt': float(tilt_of(TH[Q])),
        'theta': float(TH[Q]), 'center': [float(v) for v in C[Q]],
        'non_deepest': non_deepest, 'depth_max_other': max(others) if others else None,
        'n_intruders_at_corner': len(cst[cn]['intruders']),
        'argmin': [[float(p[0]), float(p[1])] for p in A],
        'K': K, 'cardinals': cards,
        'contacts': [{'kind': r['kind'], 'other': r['other'],
                      'n': [float(r['n'][0]), float(r['n'][1])],
                      'pt': [float(r['pt'][0]), float(r['pt'][1])],
                      'gap': float(r['gap']), 'type': r['type'],
                      'n_admissible': int(r['n_admissible'])} for r in rows],
        'n_contacts': len(rows),
        'lock': lock_lp(rows, C[Q]),
        'menu': menu_status(Q, C, TH, rows, wcs),
    }
    dl = signed_tilt(TH[Q])
    out['lock_away_from_flush'] = bool(
        out['lock']['plus'] if dl > 0 else out['lock']['minus']) \
        if abs(dl) > 1e-9 else None
    out['LOCKED'] = bool(out['lock']['selfstress']
                         or (out['lock_away_from_flush'] is True))
    if not want_clusters:
        return out
    cl = {}
    for lbl in cards + ['(1,1)']:
        vfr = {'e_x': np.array([1.0, 0.0]), 'e_y': np.array([0.0, 1.0]),
               '(1,1)': np.array([1.0, 1.0])}[lbl]
        ew = vec_to_world(vfr, fr)
        mem, edges = cluster(Q, ew, pcs)
        wa, wh = wall_anchored(mem, ew, wcs)
        ia, ih = intruder_anchored(mem, ew, cst, cn, C, TH, bbox)
        # per-contact side report for this e
        sides = []
        for r in rows:
            sides.append({'other': r['other'], 'kind': r['kind'],
                          'ndote': float(r['n'] @ ew),
                          'blocking': bool(float(r['n'] @ ew) < 0.0)})
        cl[lbl] = {'e_world': [float(ew[0]), float(ew[1])],
                   'members': mem, 'size': len(mem), 'edges': edges,
                   'wall_anchored': wa, 'wall_hits': wh,
                   'intruder_anchored': ia, 'intruder_hits': ih,
                   'free': bool(not wa and not ia), 'sides': sides}
    out['clusters'] = cl
    # RETREATABLE uses only the CARDINAL directions (the theory lead's definition)
    out['RETREATABLE'] = bool(any(cl[lbl]['free'] for lbl in cards))
    out['diag_free'] = bool(cl['(1,1)']['free'])
    return out


def res_of(C, TH, s, bbox=None, want_clusters=True):
    """RES(z): every non-deepest intruder at every corner is NOT retreatable."""
    if bbox is None:
        bbox = tight_bbox_of(C, TH)
    cst = corner_state(C, TH, bbox)
    pcs = all_pair_contacts(C, TH)
    wcs = wall_contacts(C, TH, s)
    items = []
    for cn in CORNERS:
        intr = cst[cn]['intruders']
        if len(intr) < 2:
            continue
        for Q in intr:
            # non-deepest: some OTHER square has depth >= Q's (ties count for both)
            if any(float(cst[cn]['depth'][j]) >= float(cst[cn]['depth'][Q])
                   for j in intr if j != Q):
                items.append(analyse_square(Q, cn, C, TH, s, bbox, cst, pcs,
                                            wcs, want_clusters))
    return {'n_block': [cst[c]['n_block'] for c in CORNERS],
            'items': items,
            'RES': bool(all(not it.get('RETREATABLE') for it in items)),
            'n_nondeepest': len(items),
            'n_retreatable': sum(1 for it in items if it.get('RETREATABLE'))}


def unpack_x(x):
    c, th, s = cp85.unpack(x)
    return np.asarray(c, float), np.asarray(th, float), float(s)


def unpack_z(z):
    z = np.asarray(z, float)
    C = np.stack([z[0:33:3], z[1:33:3]], axis=1)
    return C, z[2:33:3].copy(), float(z[33])


# ============================================================ task 1: exits

def flow_free_capture(x0, rounds=KD.ROUNDS_FREE, delta0=KD.TRUST0):
    """k0dir87.sqp_flow(keep_k0=False) with the bisected exit point returned."""
    x, cur, ov, cv = KD.strictify(x0)
    em = None
    xe = None
    nstep = 0
    delta = delta0
    for _r in range(rounds):
        if delta < KD.TRUST_MIN:
            break
        y, _sel = KD.sqp_step(x, False, delta)
        if y is None:
            delta *= 0.4
            continue
        ws, sg, good, blk = KD._blocked_feasible(y)
        if not good or sg > cur - 1e-12:
            delta *= 0.4
            continue
        if not blk:
            # k0dir87._exit_record inlined so the OTHER bisection endpoint
            # (the first configuration that is no longer K0-BLOCKED) is kept too
            a, b = KD._bisect_exit_t(x, y)
            xe, sge, ok_e, blk_e = a
            xb, sgb, ok_b, _bb = b
            st0 = KD.k0_state(xe)
            st1 = KD.k0_state(xb)
            em = KD.exit_mode(st0, st1)
            em['sigma_exit'] = float(sge)
            em['sigma_after_exit'] = float(sgb)
            em['exit_feasible'] = bool(ok_e)
            em['exit_blocked'] = bool(blk_e)
            em['n_block_exit'] = st0['n_block']
            em['n_block_after'] = st1['n_block']
            em['m1_exit'] = [float(v) for v in st0['m1']]
            em['m2_exit'] = [float(v) for v in st0['m2']]
            return x, em, xe, nstep, xb
        x = ws
        cur = sg
        nstep += 1
        delta = min(delta0, delta * 1.6)
    return x, em, xe, nstep, None


def prime_pool(log=print):
    """k0dir87's campaign is `main('run')` = selftest -> canary -> run.  selftest
    calls build_seed with rng = random.Random(12345), which is what populates the
    module-global corner-pair _POOL; run()'s own rng = random.Random(20260903)
    then never pays for the pool.  So the pool must be primed the same way before
    the run stream is replayed."""
    if KD._POOL is None:
        t0 = time.time()
        KD.selftest(log=lambda *a: None)
        log('pool primed via k0dir87.selftest (%d pairs, %.0fs)'
            % (len(KD._POOL), time.time() - t0))


def seed_stream(nmax=520):
    """Exactly k0dir87.run()'s rng stream: random.Random(20260903), then per tag
    up to 40 build_seed calls until one succeeds."""
    prime_pool()
    rng = random.Random(20260903)
    for i in range(nmax):
        tag = 's%04d' % i
        x0 = None
        for _ in range(40):
            x0 = KD.build_seed(rng)
            if x0 is not None:
                break
        yield tag, x0


def stored_exits():
    path = os.path.join(A87, 'results', 'k0dir87.jsonl')
    out = {}
    for ln in open(path):
        if not ln.strip():
            continue
        r = json.loads(ln)
        out[r['tag']] = r
    return out


def exit_motion(xe, xb, Q):
    """What the flow ACTUALLY did across the exit: per-square translation and
    rotation between the two bisection endpoints."""
    C0, T0, s0 = unpack_x(xe)
    C1, T1, s1 = unpack_x(xb)
    dc = np.linalg.norm(C1 - C0, axis=1)
    dt = np.abs(T1 - T0)
    scale = max(float(dc.max()), float(dt.max()), 1e-300)
    mov = [int(i) for i in range(N) if dc[i] > 0.05 * scale or dt[i] > 0.05 * scale]
    return {'ds': float(s1 - s0),
            'dc': [float(v) for v in dc], 'dth': [float(v) for v in dt],
            'linf': float(scale),
            'n_squares_moving': len(mov), 'moving': mov,
            'Q_dc': float(dc[Q]), 'Q_dth': float(dt[Q]),
            'Q_dc_rel': float(dc[Q] / scale), 'Q_dth_rel': float(dt[Q] / scale),
            'Q_is_sole_mover': bool(mov == [Q]),
            'rotation_dominates_Q': bool(dt[Q] > dc[Q]),
            'dc_max_other': float(max([dc[i] for i in range(N) if i != Q])),
            'dth_max': float(dt.max())}


def exit_analysis(tag, em, xe, xb=None):
    C, TH, s = unpack_x(xe)
    bbox = tight_bbox_of(C, TH)
    cst = corner_state(C, TH, bbox)
    pcs = all_pair_contacts(C, TH)
    wcs = wall_contacts(C, TH, s)
    rec = {'tag': tag, 'sigma_exit': em['sigma_exit'],
           'corners_freed': em['corners_freed'],
           'mode': em['mode'], 'n_block_exit': em['n_block_exit'],
           'n_block_after': em['n_block_after'],
           'n_block_recomputed': [cst[c]['n_block'] for c in CORNERS],
           'blockers': []}
    for md in em['modes']:
        cn = md['corner']
        lost = md['lost']
        for Q in lost:
            a = analyse_square(int(Q), cn, C, TH, s, bbox, cst, pcs, wcs)
            a['exit_lost_from'] = cn
            a['kept_at_corner'] = md['kept']
            if xb is not None:
                a['motion'] = exit_motion(xe, xb, int(Q))
            rec['blockers'].append(a)
    rec['x_ok'] = [float(v) for v in xe]
    if xb is not None:
        rec['x_bad'] = [float(v) for v in xb]
    return rec


def cmd_check3(log=print):
    st = stored_exits()
    n = 0
    ok = True
    for tag, x0 in seed_stream(3):
        if x0 is None:
            log('%s seed_failed' % tag)
            continue
        _x, em, _xe, nst = flow_free_capture(x0)
        ref = st[tag]['free_exit']
        d = abs(em['sigma_exit'] - ref['sigma_exit']) if em else float('inf')
        same = (em is not None and em['corners_freed'] == ref['corners_freed']
                and em['mode'] == ref['mode'] and d < 1e-9)
        ok = ok and same
        log('%s sigma_exit %.12f vs stored %.12f  |d| %.2e  freed %s vs %s  %s'
            % (tag, em['sigma_exit'] if em else float('nan'), ref['sigma_exit'],
               d, em['corners_freed'] if em else None, ref['corners_freed'],
               'OK' if same else 'MISMATCH'))
        n += 1
    log('check3: %s (%d seeds)' % ('PASS' if ok else 'FAIL', n))
    return ok


def cmd_task1(nmax=520, log=print):
    st = stored_exits()
    t0 = time.time()
    out = []
    nmis = 0
    path = os.path.join(RESULTS, 't3_exits.jsonl')
    with open(path, 'w') as fh:
        for tag, x0 in seed_stream(nmax):
            if x0 is None:
                log('%s seed_failed' % tag)
                continue
            _x, em, xe, _n, xb = flow_free_capture(x0)
            if em is None:
                log('%s no exit' % tag)
                continue
            ref = st.get(tag, {}).get('free_exit')
            match = bool(ref and abs(em['sigma_exit'] - ref['sigma_exit']) < 1e-9
                         and em['corners_freed'] == ref['corners_freed'])
            if not match:
                nmis += 1
            rec = exit_analysis(tag, em, xe, xb)
            rec['reproduces_stored'] = match
            fh.write(json.dumps(rec) + '\n')
            fh.flush()
            out.append(rec)
            if len(out) % 25 == 0:
                log('  %d exits, %.0fs, %d mismatches' % (len(out), time.time() - t0, nmis))
    log('task1: %d exit events, %d mismatches, %.0fs -> %s'
        % (len(out), nmis, time.time() - t0, path))
    return out


# ====================================================== task 2: the 4 endpoints

def cmd_task2(log=print):
    path = os.path.join(A87, 'results', 'k0dir87.polish.jsonl')
    rows = [json.loads(l) for l in open(path) if l.strip()]
    pts = [r for r in rows if r.get('exact_K0_BLOCKED') and r.get('z_polished')]
    log('task2: %d polished K0-BLOCKED non-FJ endpoints' % len(pts))
    out = []
    for r in pts:
        z = np.array([float(Fraction(v)) for v in r['z_polished']])
        C, TH, s = unpack_z(z)
        rs = res_of(C, TH, s)
        # certified Gordan descent direction from the FJ NNLS residual
        rows_a, _info = F.classify(z, 1e-6)
        A = F.gradA(z, rows_a)
        res, lam, y = F.cone_nnls(A)          # y = A_n^T lam - e_s (Gordan dir)
        chk = A @ y
        ent = {'tag': r['tag'], 'sigma': r['sigma_polished'],
               'exact_n_block': r['exact_n_block'],
               'n_block_float': rs['n_block'],
               'cone_residual': float(res), 'm_active': len(rows_a),
               'gordan_min_Ay': float(chk.min()), 'gordan_ds': float(y[33]),
               'RES': rs['RES'], 'n_nondeepest': rs['n_nondeepest'],
               'n_retreatable': rs['n_retreatable'],
               'items': rs['items']}
        # does y decrease the depth of a non-deepest intruder?
        h = 1e-7
        zz = z + h * y
        C2, TH2, _s2 = unpack_z(zz)
        bbox = tight_bbox_of(C, TH)
        moved = []
        for it in rs['items']:
            Q = it['sq']
            cn = it['corner']
            fr = frame(bbox, cn)         # container/anchors FROZEN
            d0, _f, _A = depth_arg(verts(C[Q], TH[Q]), fr)
            d1, _f, _A = depth_arg(verts(C2[Q], TH2[Q]), fr)
            moved.append({'sq': Q, 'corner': cn, 'd0': float(d0),
                          'dd_dt': float((d1 - d0) / h),
                          'decreases': bool((d1 - d0) / h < -1e-9),
                          'RETREATABLE': it['RETREATABLE'],
                          'non_deepest': it['non_deepest']})
        ent['gordan_moves'] = moved
        ent['gordan_decreases_some_nondeepest'] = bool(
            any(m['decreases'] for m in moved))
        out.append(ent)
        log('  %s sigma %.9f  RES %s  nondeepest %d retreatable %d  '
            'cone_res %.3e  Gordan decreases a non-deepest depth: %s'
            % (r['tag'], r['sigma_polished'], rs['RES'], rs['n_nondeepest'],
               rs['n_retreatable'], res, ent['gordan_decreases_some_nondeepest']))
    json.dump(out, open(os.path.join(RESULTS, 't3_endpoints.json'), 'w'), indent=1)
    return out


# ============================================================= task 3: Trump

def cmd_task3(log=print):
    x = KD.trump_x()
    C, TH, s = unpack_x(x)
    bbox = tight_bbox_of(C, TH)
    cst = corner_state(C, TH, bbox)
    pcs = all_pair_contacts(C, TH)
    wcs = wall_contacts(C, TH, s)
    out = {'sigma': float(KD.enclosing_side_x(x)),
           'n_block': [cst[c]['n_block'] for c in CORNERS],
           'intruders': {c: cst[c]['intruders'] for c in CORNERS},
           'depths': {c: {int(i): float(cst[c]['depth'][i])
                          for i in cst[c]['intruders']} for c in CORNERS}}
    log('Trump sigma %.12f  n_block %s' % (out['sigma'], out['n_block']))
    for c in CORNERS:
        log('  %s intruders %s depths %s' % (c, cst[c]['intruders'],
                                             ['%.6f' % cst[c]['depth'][i]
                                              for i in cst[c]['intruders']]))
    sq = {}
    for Q in cst['TL']['intruders']:
        a = analyse_square(int(Q), 'TL', C, TH, s, bbox, cst, pcs, wcs)
        # also the (1,1) cluster
        fr = cst['TL']['frame']
        ew = vec_to_world(np.array([1.0, 1.0]), fr)
        mem, edges = cluster(int(Q), ew, pcs)
        wa, wh = wall_anchored(mem, ew, wcs)
        ia, ih = intruder_anchored(mem, ew, cst, 'TL', C, TH, bbox)
        a['cluster_diag'] = {'e_world': [float(ew[0]), float(ew[1])],
                             'members': mem, 'size': len(mem),
                             'wall_anchored': wa, 'wall_hits': wh,
                             'intruder_anchored': ia, 'intruder_hits': ih,
                             'free': bool(not wa and not ia)}
        sq[int(Q)] = a
        log('  sq%d depth %.6f tilt %.4f deg  non_deepest %s  K %s  cardinals %s'
            % (Q, a['depth'], math.degrees(a['tilt']), a['non_deepest'],
               a['K'], a['cardinals']))
        for lbl, cl in a.get('clusters', {}).items():
            log('     C_%s size %d members %s wall_anchored %s intruder_anchored %s'
                % (lbl, cl['size'], cl['members'], cl['wall_anchored'],
                   cl['intruder_anchored']))
        log('     C_(1,1) size %d wall_anchored %s'
            % (a['cluster_diag']['size'], a['cluster_diag']['wall_anchored']))
        log('     LOCK %s  MENU %s  RETREATABLE %s'
            % (a['lock'], a['menu'].get('MENU_LOCKED', a['menu'].get('reason')),
               a.get('RETREATABLE')))
    out['TL'] = sq
    rs = res_of(C, TH, s)
    out['RES'] = rs['RES']
    out['res_items'] = rs['items']
    # FJ certificate
    z = F.canonical(KD.x_to_z(x))
    v = F.verdict(z, 'trump')
    out['fj'] = {'sigma': v['sigma'], 'fj_at_tight_tol': v['fj_at_tight_tol'],
                 'fj_feasible_any_tol': v['fj_feasible_any_tol'],
                 'ladder': [{k: e.get(k) for k in
                             ('tol', 'm_active', 'cone_residual', 'fj_feasible',
                              'support', 'rank', 'rank33', 'n_rattlers')}
                            for e in v['ladder']]}
    log('Trump FJ at tight tol: %s  cone residual %s'
        % (v['fj_at_tight_tol'], v['ladder'][0].get('cone_residual')))
    log('RES(Trump) = %s  (non-deepest intruders: %d, retreatable: %d)'
        % (rs['RES'], rs['n_nondeepest'], rs['n_retreatable']))
    json.dump(out, open(os.path.join(RESULTS, 't3_trump.json'), 'w'), indent=1,
              default=float)
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'check3'
    if cmd == 'check3':
        sys.exit(0 if cmd_check3() else 1)
    elif cmd == 'task1':
        cmd_task1(int(sys.argv[2]) if len(sys.argv) > 2 else 520)
    elif cmd == 'task2':
        cmd_task2()
    elif cmd == 'task3':
        cmd_task3()
    else:
        print('unknown command %r' % cmd)
        sys.exit(2)
